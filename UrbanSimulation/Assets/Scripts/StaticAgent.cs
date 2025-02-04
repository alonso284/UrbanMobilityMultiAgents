using System.Collections.Generic;
using UnityEngine;

public class StaticAgent : MonoBehaviour
{
    // Circle prefab with a Renderer (like a sphere or disc)
    public GameObject circlePrefab;

    // Dictionary to store circles for each agent ID
    private Dictionary<int, GameObject> agentCircles = new Dictionary<int, GameObject>();

    // Mock API response
    private Dictionary<int, AgentData> apiResponse = new Dictionary<int, AgentData>
    {
        { 1, new AgentData { x = 0, y = 0, status = true } },
        { 2, new AgentData { x = 6, y = 6, status = false } },
        { 3, new AgentData { x = 6, y = 14, status = true } }
    };

    // Class to hold the API data
    [System.Serializable]
    public class AgentData
    {
        public float x;
        public float y;
        public bool status;
    }

    private void Start()
    {
        // Initialize the circles (mock API call simulation)
        UpdateCircles(apiResponse);
    }

    public void UpdateCircles(Dictionary<int, AgentData> agents)
    {
        foreach (var agent in agents)
        {
            int agentId = agent.Key;
            AgentData data = agent.Value;

            if (!agentCircles.ContainsKey(agentId))
            {
                // Instantiate a new circle (e.g., sphere) at the position
                Vector3 position = new Vector3(data.x, 0, data.y); // 3D position (x, 0, z)
                GameObject newCircle = Instantiate(circlePrefab, position, Quaternion.identity);
                newCircle.name = $"Agent {agentId}";
                agentCircles[agentId] = newCircle;
            }

            // Update the color of the circle
            UpdateCircleColor(agentCircles[agentId], data.status);
        }
    }

    private void UpdateCircleColor(GameObject circle, bool status)
    {
        Renderer renderer = circle.GetComponent<Renderer>();
        if (renderer != null)
        {
            renderer.material.color = status ? Color.green : Color.red;
        }
    }
}
