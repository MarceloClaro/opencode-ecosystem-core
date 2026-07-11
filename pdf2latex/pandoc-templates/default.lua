--[[
Template Lua Pandoc — Fallback genérico
Usado quando não há template específico para o formato.
--]]

local vars = {}

function Meta(meta)
  vars.title = meta.title and pandoc.utils.stringify(meta.title) or "Documento"
  vars.author = meta.author and pandoc.utils.stringify(meta.author) or "Extraído automaticamente"
  vars.date = meta.date and pandoc.utils.stringify(meta.date) or "\\today"
  vars.lang = meta.lang and pandoc.utils.stringify(meta.lang) or "pt-BR"
  return meta
end

function Doc(body, meta, templates)
  local documentclass = "article"
  local packages = [[
\\usepackage[utf8]{inputenc}
\\usepackage[T1]{fontenc}
\\usepackage[brazil]{babel}
\\usepackage{graphicx}
\\usepackage{amsmath,amssymb}
\\usepackage{hyperref}
\\usepackage{geometry}
\\geometry{a4paper, margin=2.5cm}
\\usepackage{setspace}
\\onehalfspacing
]]

  local header = [[
\\documentclass[12pt,a4paper]{]] .. documentclass .. [[}
]] .. packages .. [[

\\hypersetup{colorlinks=true, linkcolor=blue, citecolor=blue, urlcolor=blue}

\\title{]] .. vars.title .. [[}
\\author{]] .. vars.author .. [[}
\\date{]] .. vars.date .. [[}

\\begin{document}
\\maketitle
\\tableofcontents
\\newpage
]]

  local footer = [[
\\end{document}
]]

  return header .. body .. footer
end

return {
  {Meta = Meta},
  {Doc = Doc}
}
