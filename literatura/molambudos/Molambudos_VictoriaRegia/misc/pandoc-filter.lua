-- pandoc-filter.lua — Filtro para converter LaTeX do Molambudos para ePub
-- Remove/redefine comandos customizados que o pandoc não entende

-- Função auxiliar: extrair conteúdo de um comando LaTeX
local function get_content(node)
  if node.t == "RawInline" and node.format == "tex" then
    return node.text
  end
  return ""
end

-- Processa RawInline (comandos LaTeX)
function RawInline(el)
  local tex = el.text

  -- \lettrine[opts]{A}{bc} → "Abc"
  local a, b = tex:match("^\\lettrine(?:%[.-%])?{(.-)}{(.-)}$")
  if a and b then
    return pandoc.Str(a .. b)
  end

  -- \textcolor{color}{text} → "text"  
  local color_content = tex:match("^\\textcolor{.-}{(.-)}$")
  if color_content then
    return pandoc.Str(color_content)
  end
  
  -- \color{color} → strip
  if tex:match("^\\color{") then
    return {}
  end

  -- \fragicon{x} → strip (ícone decorativo)
  if tex:match("^\\fragicon") then
    return {}
  end

  -- \passaporte{id}{title}{year} → "✦ id title (year)"
  local p1, p2, p3 = tex:match("^\\passaporte{(.-)}{(.-)}{(.-)}$")
  if p1 then
    return pandoc.Str("✦ " .. p1 .. " " .. p2 .. " (" .. p3 .. ")")
  end
  
  -- \passaportecont{id}{title}{year}
  local c1, c2, c3 = tex:match("^\\passaportecont{(.-)}{(.-)}{(.-)}$")
  if c1 then
    local yr = (c3 ~= "") and " (" .. c3 .. ")" or ""
    return pandoc.Str("● " .. c1 .. " " .. c2 .. yr)
  end
  
  -- \passaporteluc{id}{title}{year}
  local l1, l2, l3 = tex:match("^\\passaporteluc{(.-)}{(.-)}{(.-)}$")
  if l1 then
    local yr = (l3 ~= "") and " (" .. l3 .. ")" or ""
    return pandoc.Str("★ " .. l1 .. " " .. l2 .. yr)
  end

  -- \passaportedoc{id}{title}{year}
  local d1, d2, d3 = tex:match("^\\passaportedoc{(.-)}{(.-)}{(.-)}$")
  if d1 then
    local yr = (d3 ~= "") and " (" .. d3 .. ")" or ""
    return pandoc.Str("◆ " .. d1 .. " " .. d2 .. yr)
  end

  -- \markboth{...}{...} → strip
  if tex:match("^\\markboth{") then
    return {}
  end

  -- \noindent → strip
  if tex:match("^\\noindent") then
    return {}
  end

  -- \textquotedbl → "
  if tex:match("^\\textquotedbl") then
    return pandoc.Str("\"")
  end
  
  -- \textquoteleft / \textquoteright
  if tex:match("^\\textquoteleft") then
    return pandoc.Str("'")
  end
  if tex:match("^\\textquoteright") then
    return pandoc.Str("'")
  end

  -- \textendash → –
  if tex:match("^\\textendash") then
    return pandoc.Str("–")
  end
  
  -- \textemdash → —
  if tex:match("^\\textemdash") then
    return pandoc.Str("—")
  end

  -- \hfill → space
  if tex:match("^\\hfill") then
    return pandoc.Str(" ")
  end

  -- \hspace / \vspace / \vspace* → strip
  if tex:match("^\\vh?space") then
    return {}
  end

  -- \thispagestyle → strip
  if tex:match("^\\thispagestyle") then
    return {}
  end

  -- \addcontentsline → strip
  if tex:match("^\\addcontentsline") then
    return {}
  end

  -- \dotfill → strip
  if tex:match("^\\dotfill") then
    return {}
  end

  -- \rule → strip
  if tex:match("^\\rule") then
    return {}
  end

  -- \pgfornament → strip
  if tex:match("^\\pgfornament") then
    return {}
  end

  -- \cleardoublepage / \clearpage / \newpage → horizontal rule (page break)
  if tex:match("^\\cleardoublepage") or tex:match("^\\clearpage") or tex:match("^\\newpage") then
    return pandoc.HorizontalRule()
  end

  -- \par → line break
  if tex:match("^\\par") then
    return pandoc.LineBreak()
  end

  -- \textbf{} → handled natively by pandoc
  -- \textit{} → handled natively by pandoc

  -- ~ (non-breaking space) → space
  if tex:match("^~$") then
    return pandoc.Str(" ")
  end

  return nil
end

-- Processa RawBlock (comandos em nível de bloco)
function RawBlock(el)
  local tex = el.text

  -- TikZ picture → strip (não suportado em ePub)
  if tex:match("^\\begin{tikzpicture}") then
    return {}
  end

  -- Environments to strip
  if tex:match("^\\begin{") then
    return {}
  end

  return nil
end

-- Processa Divs (ambientes LaTeX)
function Div(el)
  -- Remove divs vazios ou decorativos
  return nil
end

return {
  { RawInline = RawInline },
  { RawBlock = RawBlock },
  { Div = Div }
}
