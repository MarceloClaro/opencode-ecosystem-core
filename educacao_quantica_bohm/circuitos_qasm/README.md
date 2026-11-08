# Circuitos OpenQASM 2.0

Estes arquivos são os circuitos usados no livro. Eles podem ser colados no
editor de circuitos da Tiangong:

1. Abra <https://tiangongqs.com/cloud/circuit>.
2. Entre na sua conta.
3. Escolha o editor **QASM** (OpenQASM 2.0).
4. Cole o conteúdo de um arquivo desta pasta.
5. Selecione o backend. No console de novembro de 2026, o selecionado era
   **`Guoji No.8 (simulate)`** (20 qubits); `Baihua` (156) e vários simuladores
   também estavam listados.
6. Defina 1024 tiros e execute.
7. Compare os counts com a tabela da lauda correspondente.

| Arquivo | Experimento | O que esperar |
|---|---|---|
| `bell.qasm` | Bell | 00 e 11 dominam; 01 e 10 são ruído |
| `ghz4.qasm` | GHZ de 4 qubits | 0000 e 1111 dominam; ~21% fora no backend Guoji08 |
| `chsh_e00.qasm` | CHSH E00 | correlação positiva |
| `chsh_e01.qasm` | CHSH E01 | correlação positiva |
| `chsh_e10.qasm` | CHSH E10 | correlação positiva |
| `chsh_e11.qasm` | CHSH E11 | correlação negativa |
| `vqc_xor_00.qasm` | VQC XOR 00 | P(1) baixo |
| `vqc_xor_01.qasm` | VQC XOR 01 | P(1) alto |
| `vqc_xor_10.qasm` | VQC XOR 10 | P(1) alto |
| `vqc_xor_11.qasm` | VQC XOR 11 | P(1) baixo |

> **Limite:** o editor pode exigir login, fila e backend disponível. O arquivo
> QASM é compatível com OpenQASM 2.0; isso não é uma garantia de execução
> imediata nem de resultado idêntico. A calibração muda. O rótulo
> `(simulate)` do console pode indicar um backend simulado; confirme o tipo
> antes de chamar o resultado de “hardware”.