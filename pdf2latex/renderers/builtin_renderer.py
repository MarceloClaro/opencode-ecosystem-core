"""
Renderer Built-in — gera LaTeX usando o LaTeXGenerator existente.
Não requer dependências externas além do próprio pdf2latex.
"""

from pathlib import Path

from .base import BaseRenderer, RenderInput
from ..latex_generator import LaTeXGenerator
from ..template_integrator import TemplateIntegrator


class BuiltinRenderer(BaseRenderer):
    """
    Renderizador usando LaTeXGenerator + TemplateIntegrator.
    Mesmo pipeline da versão original, sem dependências extras.
    """

    name = "builtin"
    description = "Renderer nativo: LaTeXGenerator + TemplateIntegrator. Sem dependências extras."

    def render(self, data: RenderInput) -> Path:
        """Renderiza usando o LaTeXGenerator."""
        output_dir = data.output_dir or Path(f"./{data.pdf_name}_latex")

        generator = LaTeXGenerator(
            output_dir=output_dir,
            pdf_name=data.pdf_name,
            text_content=data.text_content,
            structure=data.structure,
            images=data.images,
            tables=data.tables,
            equations=data.equations,
            references=data.references,
        )
        generator.generate()

        # Aplicar template
        if data.template:
            integrator = TemplateIntegrator(
                project_dir=output_dir,
                template_name=data.template,
            )
            integrator.apply()

        return output_dir

    def is_available(self) -> bool:
        return True
