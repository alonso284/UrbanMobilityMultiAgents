# Simulador de Mobilidad Urbana con Multiagentes

El objetivo de la investigación es diseñar y evaluar un modelo de movilidad urbana basado en sistemas multiagente para maximizar el flujo vehicular en una ciudad pequeña, analizando el impacto de diferentes estrategias de gestión de tráfico en la eficiencia del transporte diario.

El software simulará un escenario con casas y destinos, donde agentes móviles eligen entre caminar o usar un vehículo para llegar a su destino asignado al inicio de la simulación.	


## Parámtros para evaluar flujo vehicular

**Eficiencia del flujo vehicular y peatonal**
  - Tiempo promedio de viaje: Tiempo que toma a un vehículo desplazarse de su origen a su destino.
  - Velocidad promedio: Velocidad efectiva de los vehículos en distintas zonas de la ciudad.
  - Índice de congestión: Número de vehículos en tramos específicos dividido entre la capacidad del tramo.

**Uso de infraestructura**
  - Porcentaje de uso de calles principales y secundarias
  - Tasa de ocupación de intersecciones
  - Tiempo de espera en intersecciones

 
## Agentes
### Móviles
**Peatones**

Los agentes de peatones son agentes inteligentes puramente reactivos. Son agentes basados en el objetivo ya que tienen un destino al que quieren llegar.

**Vehículos**

Los agentes de vehículos son igualmente agentes inteligentes puramente reactivos. Tienen un origen y un destino, el cúal es su objetivo. Por lo tanto, son agentes basados en el objetivo.

### Inmóviles
Semáforos
Agentes triviales (no inteligentes) con dos posibles estados lo cuales cambian acorde al tiempo.

