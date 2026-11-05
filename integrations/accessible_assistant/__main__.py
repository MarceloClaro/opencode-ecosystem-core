"""CLI do assistente acessível: UIA, voz e memória de 24 h."""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

from . import dialog, memory, routine, voice, windows_uia


def _emit(payload: dict) -> int:
    print(json.dumps(payload, ensure_ascii=False, indent=2))
    return 0 if payload.get("ok", True) else 1


def _parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(prog="accessible-assistant", description=__doc__)
    sub = parser.add_subparsers(dest="command", required=True)
    win = sub.add_parser("windows")
    win_sub = win.add_subparsers(dest="windows_command", required=True)
    win_sub.add_parser("list")
    for name in ("snapshot", "read", "read-text", "focus", "focused"):
        item = win_sub.add_parser(name)
        if name != "focused":
            item.add_argument("--window", required=True)
    click = win_sub.add_parser("click")
    click.add_argument("--window", required=True)
    click.add_argument("--name", required=True)
    click.add_argument("--confirm", action="store_true")
    type_cmd = win_sub.add_parser("type")
    type_cmd.add_argument("--window", required=True)
    type_cmd.add_argument("--name", required=True)
    type_cmd.add_argument("--text", required=True)
    type_cmd.add_argument("--confirm", action="store_true")
    write = win_sub.add_parser("write")
    write.add_argument("--text", required=True)
    write.add_argument("--confirm", action="store_true")
    press = win_sub.add_parser("press")
    press.add_argument("--confirm", action="store_true")

    say = sub.add_parser("say")
    say.add_argument("--text", required=True)
    listen = sub.add_parser("listen")
    listen.add_argument("--seconds", type=int, default=5)
    loop = sub.add_parser("voice")
    loop.add_argument("--seconds", type=int, default=5)
    loop.add_argument("--once", action="store_true")
    routine_cmd = sub.add_parser("routine")
    routine_cmd.add_argument("--interval", type=int, default=10)
    routine_cmd.add_argument("--hours", type=float, default=24.0)
    routine_cmd.add_argument("--voice-seconds", type=int, default=5)
    routine_cmd.add_argument("--once", action="store_true")

    mem = sub.add_parser("memory")
    mem_sub = mem.add_subparsers(dest="memory_command", required=True)
    mem_sub.add_parser("summary")
    mem_sub.add_parser("prune")
    mem_sub.add_parser("forget")
    sub.add_parser("config")
    return parser


def _speak_safe(text: str) -> None:
    try:
        voice.speak(text)
    except voice.VoiceError:
        pass


def voice_loop(seconds: int = 5, once: bool = False) -> int:
    mem = memory.ActivityMemory()
    _speak_safe("Assistente acessível pronto. Diga Core para um comando.")
    iterations = 0
    while True:
        iterations += 1
        try:
            path = voice.record(seconds)
            if not voice.has_speech(path):
                if once:
                    return _emit({"ok": True, "heard": False, "reason": "silence"})
                continue
            text = voice.transcribe(path)
        except voice.VoiceError as exc:
            return _emit({"ok": False, "error": {"code": exc.code, "message": exc.message}})
        mem.append("voice", text)
        command = dialog.parse_command(text)
        intent = command.get("intent")
        if intent == "ambient":
            if once:
                return _emit({"ok": True, "heard": True, "text": text, "intent": "ambient"})
            continue
        if intent == "stop":
            _speak_safe("Encerrando o assistente.")
            return _emit({"ok": True, "stopped": True, "text": text})
        try:
            if intent == "read":
                data = windows_uia.read_text_focused()
                text = (data.get("data") or {}).get("text", "")
                _speak_safe(text[:600] or "Não encontrei texto na janela.")
            elif intent == "click":
                target = command.get("target", "")
                _speak_safe(f"Confirma clicar em {target}? Diga sim.")
                answer = voice.transcribe(voice.record(3))
                mem.append("confirmation", answer)
                if dialog.is_confirmation(answer):
                    focused = windows_uia.focused()
                    window = focused["data"]["window"]
                    windows_uia.invoke(window, target, confirmed=True)
                    mem.append("action", "click", window=window, target=target)
                    _speak_safe("Clique enviado.")
                else:
                    _speak_safe("Cancelado.")
            elif intent == "write":
                content = command.get("text", "")
                _speak_safe("Confirma escrever o texto? Diga sim.")
                answer = voice.transcribe(voice.record(3))
                mem.append("confirmation", answer)
                if dialog.is_confirmation(answer):
                    windows_uia.set_focused(content, confirmed=True)
                    mem.append("action", "write", chars=len(content))
                    _speak_safe("Texto escrito.")
                else:
                    _speak_safe("Cancelado.")
            elif intent == "press":
                _speak_safe("Confirma acionar o elemento em foco? Diga sim.")
                answer = voice.transcribe(voice.record(3))
                mem.append("confirmation", answer)
                if dialog.is_confirmation(answer):
                    windows_uia.invoke_focused(confirmed=True)
                    mem.append("action", "press")
                    _speak_safe("Acionado.")
                else:
                    _speak_safe("Cancelado.")
            else:
                _speak_safe("Comando não reconhecido.")
        except windows_uia.UIAError as exc:
            _speak_safe("Não consegui: " + exc.code)
            mem.append("error", exc.code)
        if once:
            return _emit({"ok": True, "heard": True, "text": text, "intent": intent})
        if iterations >= 100000:
            return _emit({"ok": True, "stopped": True, "reason": "limit"})


def main(argv: list[str] | None = None) -> int:
    args = _parser().parse_args(argv)
    config = windows_uia.load_config()
    if args.command == "config":
        return _emit({"ok": True, "allowed_windows": config["allowed_windows"],
                      "denied_windows": config["denied_windows"],
                      "bridge_path": config["bridge_path"],
                      "external_validation": False})
    if args.command == "say":
        try:
            path = voice.speak(args.text)
        except voice.VoiceError as exc:
            return _emit({"ok": False, "error": {"code": exc.code, "message": exc.message}})
        return _emit({"ok": True, "audio": str(path), "chars": len(args.text)})
    if args.command == "voice":
        return voice_loop(args.seconds, args.once)
    if args.command == "routine":
        recorder = routine.RoutineRecorder(args.interval)
        if args.once:
            return _emit(recorder.step(args.voice_seconds))
        return _emit(recorder.run(args.hours, args.voice_seconds))
    if args.command == "listen":
        try:
            text = voice.listen_once(args.seconds)
        except voice.VoiceError as exc:
            return _emit({"ok": False, "error": {"code": exc.code, "message": exc.message}})
        memory.ActivityMemory().append("voice", text)
        return _emit({"ok": True, "text": text})
    if args.command == "memory":
        mem = memory.ActivityMemory()
        if args.memory_command == "summary":
            return _emit(mem.summary())
        if args.memory_command == "prune":
            return _emit({"ok": True, "kept": mem.prune()})
        return _emit(mem.forget())
    if args.command == "windows":
        try:
            if args.windows_command == "list":
                return _emit(windows_uia.list_windows(config))
            if args.windows_command == "snapshot":
                return _emit(windows_uia.snapshot(args.window, config))
            if args.windows_command == "read":
                return _emit(windows_uia.read(args.window, config))
            if args.windows_command == "read-text":
                return _emit(windows_uia.read_text(args.window, config))
            if args.windows_command == "focus":
                return _emit(windows_uia.focus(args.window, config))
            if args.windows_command == "focused":
                return _emit(windows_uia.focused(config))
            if args.windows_command == "click":
                result = windows_uia.invoke(args.window, args.name,
                                            confirmed=args.confirm, config=config)
                memory.ActivityMemory().append("action", "click", window=args.window, name=args.name)
                return _emit(result)
            if args.windows_command == "type":
                result = windows_uia.set_value(args.window, args.name, args.text,
                                               confirmed=args.confirm, config=config)
                memory.ActivityMemory().append("action", "type", window=args.window, name=args.name)
                return _emit(result)
            if args.windows_command == "write":
                result = windows_uia.set_focused(args.text, confirmed=args.confirm, config=config)
                memory.ActivityMemory().append("action", "write", chars=len(args.text))
                return _emit(result)
            if args.windows_command == "press":
                result = windows_uia.invoke_focused(confirmed=args.confirm, config=config)
                memory.ActivityMemory().append("action", "press")
                return _emit(result)
        except windows_uia.UIAError as exc:
            return _emit({"ok": False, "error": {"code": exc.code, "message": exc.message}})
    return _emit({"ok": False, "error": {"code": "unknown", "message": "comando desconhecido"}})


if __name__ == "__main__":
    raise SystemExit(main())
