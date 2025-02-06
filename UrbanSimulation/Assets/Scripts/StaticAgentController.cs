using System.Collections.Generic;
using UnityEngine;

public class StaticAgentController : MonoBehaviour
{
    public GameObject trafficLightPrefab; // Prefab for traffic lights
    private Dictionary<int, GameObject> agentCircles = new Dictionary<int, GameObject>(); // Tracks agents
    private List<Vector3> predefinedPositions = new List<Vector3>
    {
        new Vector3(4.5f, 1, 13), // X, Y(height), Z
        new Vector3(6, 1, 12.5f),
        new Vector3(5, 1, 14.5F),
        new Vector3(6.5f, 1, 14),
        new Vector3(4.5f, 1, 5),
        new Vector3(6, 1, 4.5f),
        new Vector3(5, 1, 6.5F),
        new Vector3(6.5f, 1, 6),
        new Vector3(4.5f, 1, 21),
        new Vector3(6, 1, 20.5f),
        new Vector3(5, 1, 22.5F),
        new Vector3(6.5f, 1, 22),
        new Vector3(4.5f, 1, 29),
        new Vector3(6, 1, 28.5f),
        new Vector3(5, 1, 30.5F),
        new Vector3(6.5f, 1, 30)
    }; // Predefined traffic light positions on XZ plane
    private Dictionary<Vector3, GameObject> positionLights = new Dictionary<Vector3, GameObject>(); // Tracks lights at predefined positions

    private void Start()
    {
        // Initialize all positions with default red spheres
        foreach (Vector3 position in predefinedPositions)
        {
            GameObject defaultLight = Instantiate(trafficLightPrefab, position, Quaternion.identity);
            Renderer renderer = defaultLight.GetComponent<Renderer>();
            if (renderer != null)
            {
                renderer.material.color = Color.red; // Default red
            }
            positionLights[position] = defaultLight;
        }
    }

    public void UpdateStaticAgents(Dictionary<int, StaticAgentData> agents)
    {
        // Reset all predefined positions to default red
        foreach (var light in positionLights.Values)
        {
            Renderer renderer = light.GetComponent<Renderer>();
            if (renderer != null)
            {
                renderer.material.color = Color.red;
            }
        }

        // Update traffic lights based on agent data
        foreach (var agent in agents)
        {
            int agentId = agent.Key;
            StaticAgentData data = agent.Value;
            Debug.Log($"Updating agent {agentId} with status {data.status}. Position: {data.x}, {data.y}, {data.z}");

            Vector3 agentPosition = new Vector3(data.x, 1, data.z); // Assume Y is 0 for traffic light placement on XZ plane

            // Find the closest predefined position
            Vector3? closestPosition = FindClosestPosition(agentPosition);
            if (closestPosition.HasValue)
            {
                if (!agentCircles.ContainsKey(agentId))
                {
                    // Link the agent to the traffic light at this position
                    agentCircles[agentId] = positionLights[closestPosition.Value];
                }

                // Update the traffic light color
                UpdateCircleColor(positionLights[closestPosition.Value], data.status);
            }
            else
            {
                Debug.LogWarning($"Agent {agentId} position {agentPosition} is not close to any predefined positions.");
            }
        }
    }

    private void UpdateCircleColor(GameObject circle, bool status)
    {
        Renderer renderer = circle.GetComponent<Renderer>();
        if (renderer != null)
        {
            Debug.Log($"Updating circle {circle.name} color to {(status ? "green" : "red")}.");
            renderer.material.color = status ? Color.green : Color.red;
        }
        else
        {
            Debug.LogError($"Renderer not found on {circle.name}");
        }
    }

    private Vector3? FindClosestPosition(Vector3 position, float tolerance = 0.5f)
    {
        foreach (Vector3 predefinedPosition in predefinedPositions)
        {
            if (Vector3.Distance(position, predefinedPosition) <= tolerance)
            {
                return predefinedPosition;
            }
        }
        return null;
    }
}
