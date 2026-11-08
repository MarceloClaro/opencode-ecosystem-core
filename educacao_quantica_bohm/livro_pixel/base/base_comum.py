# -*- coding: utf-8 -*-
"""Formato compacto da base de 100 conceitos."""


def C(pid, parte, titulo, ideia, analogia, limite, pratica, codigo,
      erro, alem, dialogo, etica, vida, checkpoint):
    return {
        "id": pid,
        "parte": parte,
        "titulo": titulo,
        "ideia": ideia,
        "analogia": analogia,
        "limite": limite,
        "pratica": pratica,
        "codigo": codigo,
        "erro": erro,
        "alem": alem,
        "dialogo": dialogo,
        "etica": etica,
        "vida": vida,
        "checkpoint": checkpoint,
    }


def Cmin(pid, parte, titulo, ideia, analogia, pratica, erro, dialogo, checkpoint):
    """Versão curta: o gerador preenche os campos ausentes com templates da parte."""
    return C(pid, parte, titulo, ideia, analogia, "", pratica, "", erro,
             "", dialogo, "", "", checkpoint)