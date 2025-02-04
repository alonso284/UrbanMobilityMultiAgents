using System.Collections.Generic;
using UnityEngine;

public class StaticAgentController : MonoBehaviour
{

    public GameObject trafficLightPrefab;

    private Dictionary<int, GameObject> agentCircles = new Dictionary<int, GameObject>();

    public void UpdateStaticAgents(Dictionary<int, StaticAgentData> agents)
    {
        foreach (var agent in agents)
        {
            int agentId = agent.Key;
            StaticAgentData data = agent.Value;

            if (!agentCircles.ContainsKey(agentId))
            {
                Vector3 position = new Vector3(data.x, data.y, data.z);
                GameObject newCircle = Instantiate(trafficLightPrefab, position, Quaternion.identity);
                newCircle.name = $"Agent {agentId}";
                agentCircles[agentId] = newCircle;
            }
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
