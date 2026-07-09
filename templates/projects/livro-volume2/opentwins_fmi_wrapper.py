import json
import math

class PeriodontalFMUWrapper:
    """
    Mock de uma Unidade Mock-up Funcional (FMU) aderente ao padrão FMI (Functional Mock-up Interface).
    Este script simula a interface de execução que o `opentwins-fmi-api` contêinerizado
    utiliza para rodar nossos pipelines biomecânicos remotamente.
    """
    def __init__(self):
        # Parâmetros de Instância FMI
        self.time = 0.0
        self.inputs = {
            "force_masticatory": 300.0,
            "angle_incidence_deg": 0.0
        }
        self.outputs = {
            "von_mises_stress": 0.0,
            "safety_factor": 0.0,
            "bone_displacement_mm": 0.0
        }
        self.parameters = {
            "implant_radius_mm": 2.0,
            "bone_elastic_limit_mpa": 130.0
        }
    
    def set_real(self, var_name, value):
        """Define variáveis de entrada (Inputs) vindas do InfluxDB pelo OpenTwins."""
        if var_name in self.inputs:
            self.inputs[var_name] = value
        elif var_name in self.parameters:
            self.parameters[var_name] = value

    def get_real(self, var_name):
        """Obtém variáveis de saída (Outputs) para retorno ao Broker MQTT do OpenTwins."""
        return self.outputs.get(var_name, 0.0)

    def do_step(self, current_time, step_size):
        """
        Calcula o próximo estado físico. Executa a Lógica Core de nosso Gêmeo Periodontal.
        """
        # Área de contato baseada no raio do implante
        radius = self.parameters["implant_radius_mm"]
        area = math.pi * (radius ** 2)
        
        # Decomposição da força baseada no ângulo de incidência
        angle_rad = math.radians(self.inputs["angle_incidence_deg"])
        effective_force = self.inputs["force_masticatory"] / math.cos(angle_rad) if math.cos(angle_rad) != 0 else self.inputs["force_masticatory"]
        
        # Cálculo da Tensão de von Mises
        stress = effective_force / area
        
        # Fator de Segurança
        elastic_limit = self.parameters["bone_elastic_limit_mpa"]
        safety_factor = elastic_limit / stress if stress > 0 else 999.9
        
        # Simulação simples de micro-deslocamento (Lei de Hooke simplificada)
        stiffness = 2000.0  # N/mm
        displacement = effective_force / stiffness
        
        # Atualiza os outputs
        self.outputs["von_mises_stress"] = round(stress, 2)
        self.outputs["safety_factor"] = round(safety_factor, 2)
        self.outputs["bone_displacement_mm"] = round(displacement, 4)
        
        self.time = current_time + step_size
        return True

if __name__ == "__main__":
    print("=== INICIANDO FMI WRAPPER SIMULATION (OPENCODE) ===")
    fmu = PeriodontalFMUWrapper()
    
    # Recebendo input externo (ex: vindo da API OpenTwins)
    fmu.set_real("force_masticatory", 350.0)
    fmu.set_real("angle_incidence_deg", 15.0)
    
    # Rodando um step de simulação (0.1 segundos)
    print(">> Executando step do FMI (Δt = 0.1s)...")
    success = fmu.do_step(0.0, 0.1)
    
    if success:
        stress = fmu.get_real("von_mises_stress")
        sf = fmu.get_real("safety_factor")
        disp = fmu.get_real("bone_displacement_mm")
        
        print("\n[RESULTADOS DO FMI]")
        print(f"Tensão de von Mises: {stress} MPa")
        print(f"Fator de Segurança: {sf}")
        print(f"Deslocamento Ósseo: {disp} mm")
    print("=== SIMULAÇÃO FMI FINALIZADA ===")
