--[[
Template Lua Pandoc — IEEE
Para conferências e transactions IEEE.
--]]

local vars = {}

function Meta(meta)
  vars.title = meta.title and pandoc.utils.stringify(meta.title) or "Document"
  vars.author = meta.author and pandoc.utils.stringify(meta.author) or "Author"
  vars.date = meta.date and pandoc.utils.stringify(meta.date) or "\\today"
  return meta
end

function Pandoc(blocks, meta)
  vars = Meta(meta) or vars

  local header = [[
\\documentclass[conference]{IEEEtran}

\\usepackage[utf8]{inputenc}
\\usepackage[T1]{fontenc}
\\usepackage{graphicx}
\\usepackage{amsmath,amssymb}
\\usepackage{booktabs}
\\usepackage{hyperref}
\\usepackage{cite}

\\title{]] .. vars.title .. [[}
\\author{]] .. vars.author .. [[}

\\begin{document}

\\maketitle
\\begin{abstract}
Documento convertido automaticamente via pdf2latex (SPEC-962).
\\end{abstract}
]]

  local footer = [[
\\bibliographystyle{IEEEtran}
\\bibliography{referencias}

\\end{document}
]]

  local body = pandoc.write(pandoc.Pandoc(blocks, meta), 'latex')
  return header .. body .. footer
end

return {{Pandoc = Pandoc}}
