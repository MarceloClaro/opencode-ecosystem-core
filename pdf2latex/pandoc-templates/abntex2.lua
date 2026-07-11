--[[
Pandoc Lua Writer — abnTeX2 (ABNT)
Para uso com: pandoc -t abntex2.lua
--]]

local vars = {}

function Meta(meta)
  vars.title = meta.title and pandoc.utils.stringify(meta.title) or "Documento"
  vars.author = meta.author and pandoc.utils.stringify(meta.author) or "Autor"
  vars.date = meta.date and pandoc.utils.stringify(meta.date) or "\\today"
  return meta
end

function Writer(doc, opts)
  Meta(doc.meta)

  local header = {}
  table.insert(header, "\\documentclass[12pt,a4paper]{abntex2}")
  table.insert(header, "")
  table.insert(header, "\\usepackage[utf8]{inputenc}")
  table.insert(header, "\\usepackage[T1]{fontenc}")
  table.insert(header, "\\usepackage[brazil]{babel}")
  table.insert(header, "\\usepackage{graphicx}")
  table.insert(header, "\\usepackage{amsmath,amssymb,amsfonts}")
  table.insert(header, "\\usepackage{booktabs}")
  table.insert(header, "\\usepackage{hyperref}")
  table.insert(header, "\\usepackage{geometry}")
  table.insert(header, "\\geometry{a4paper, margin=2.5cm}")
  table.insert(header, "\\usepackage{indentfirst}")
  table.insert(header, "\\usepackage{setspace}")
  table.insert(header, "\\usepackage{tabularx}")
  table.insert(header, "\\usepackage{longtable}")
  table.insert(header, "\\usepackage{caption}")
  table.insert(header, "\\usepackage{subcaption}")
  table.insert(header, "\\usepackage{xcolor}")
  table.insert(header, "")
  table.insert(header, "\\usepackage[alf]{abntex2cite}")
  table.insert(header, "")
  table.insert(header, "\\onehalfspacing")
  table.insert(header, "\\hypersetup{colorlinks=true, linkcolor=blue, citecolor=blue, urlcolor=blue}")
  table.insert(header, "")
  table.insert(header, "\\title{" .. vars.title .. "}")
  table.insert(header, "\\author{" .. vars.author .. "}")
  table.insert(header, "\\date{" .. vars.date .. "}")
  table.insert(header, "")
  table.insert(header, "\\begin{document}")
  table.insert(header, "")
  table.insert(header, "\\maketitle")
  table.insert(header, "\\tableofcontents")
  table.insert(header, "\\newpage")
  table.insert(header, "")

  local body = pandoc.write(doc, "latex")

  local footer = {}
  table.insert(footer, "")
  table.insert(footer, "\\bibliographystyle{abntex2-alf}")
  table.insert(footer, "\\bibliography{referencias}")
  table.insert(footer, "")
  table.insert(footer, "\\end{document}")

  return table.concat(header, "\n") .. "\n" .. body .. "\n" .. table.concat(footer, "\n")
end

return {Writer = Writer}
