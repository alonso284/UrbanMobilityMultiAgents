# Simulador de Mobilidad Urbana con Multiagentes

Modelo de movilidad urbana basado en sistemas multiagente para maximizar el flujo en una ciudad pequeña. Analiza el impacto de diferentes estrategias de gestión de tráfico en la eficiencia del transporte diario.

El software simula un escenario con casas y destinos, donde agentes móviles se mueven para llegar a su destino de la manera más eficiente. El enfoque es en la navegación de los peatones en un ambiente donde hay cruces e intersecciones con vehículos.

## Parámetros para evaluar eficiencia del flujo peatonal

- **Tiempo promedio de viaje**: Tiempo que toma a un peatón desplazarse de su origen a su destino.
- **Velocidad promedio**: Velocidad efectiva de los peatones (medida de la distancia desplazada y el tiempo tardado en llegar)
- **Tiempo de espera promedio en intersecciones**: Cantidad de pasos que pasa un peatón esperando en un cruce peatonal

## Ambiente

Una cuadrícula de tipo dinámico, discreto y accesible con distintos estados:

- **Casas** (Rojo): una cuadrícula donde habitan los agentes
- **Destinos** (Azul): lugar a donde quieren llegar los agentes
- **Calles** (Gris oscuro con flechas): lugares donde se pueden mover los agentes de vehículo
- **Banquetas** (Azul grisáceo): lugares donde se pueden mover los agentes de peatones
- **Cruces peatonales** (Activado: Gris claro, Desactivado: Blanco): lugares donde se pueden mover los agentes de vehículo y los agentes de peatones
- **Obstáculos** (Estacionamiento, obstáculo, pasto): lugares que no clasifican como ninguno de los anteriores
- 
 <img width="902" alt="Mapa" src="https://github.com/user-attachments/assets/ed5db45d-a5d1-4288-8f9e-c18d3e2e8485" />

## Agentes

- **Peatones**: Agentes inteligentes. Son agentes basados en un objetivo, llegar a su destino de la manera más eficiente.
- **Vehículos**: Agentes inteligentes puramente reactivos. Su dirección se escoge de manera aleatoria y siguen las leyes de la calle.
- **Semáforos**: Agentes triviales con dos posibles estados y una posición, los cuales cambian acorde al tiempo.

Los peatones están entrenados con Q-learning. El entrenamiento se realiza en un ambiente estático, sin importar el estado de los semáforos ni vehículos. Para mejorar la eficiencia, todos los agentes comparten el mismo Q-Table. Como el estado incluye el destino del agente, es como si cada grupo de peatones con el mismo destino tuviera su propio Q-Table

## REST API Endpoints

## /simulation_stats [GET]

Método para obtener metadatos de la simulación

```js
{
    'traffic_light_step_duration': int,
    'traffic_light_step_cooldown': int,
    'car_density': double,
    'steps': int,
    'alpha': double,
    'gamma': double,
    'epsilon': double,
    'train_episodes': 200,
    'car_id_list': [int],
    'pedestrian_id_list': [int],
    'traffic_light_id_list': [int],
}
```

## /mobile_agent_state/{step_number} [GET]

Método para obtener la ubicación de todos los agentes móbiles.

```js
[
  {
    'id': int,
    'x': int,
    'y': int,
    'type': string
  },
  ...
]
```

## /static_agent_state/{step_number} [GET]

Método para obtener la ubicación y estado de todos los agentes estáticos.

```js
[
  {
    'id': int,
    'x': int,
    'y': int,
    'status': bool // (True = Green, False = Yellow)
  },
  ...
]
```

[Simulación en Unity](https://youtu.be/i_RkS7PlOcI?si=Ht0Op3d3EGdc3jvy)
