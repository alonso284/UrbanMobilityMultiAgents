using System.Collections.Generic;
using UnityEngine;
using System.IO;

public class AgentController : MonoBehaviour
{
    // Car prefab
    public GameObject carPrefab;

    public GameObject pedestrianPrefab;

    // Dictionary to store car objects for each car ID
    private Dictionary<int, GameObject> carAgents = new Dictionary<int, GameObject>();

    private Dictionary<int, GameObject> pedestrianAgents = new Dictionary<int, GameObject>();

    // Speed of the car movement
    public float moveSpeed = 5.0f;
    public float rotationSpeed = 0.8f;
    private string[,] roadMap = {
    {"gr", "gr", "gr", "gr", "sw", "ds", "us", "sw", "gr", "gr", "gr", "gr", "sw", "ds", "us", "sw", "gr", "gr", "ho", "dw", "sw", "ds", "us", "sw", "gr", "gr", "de", "dw", "sw", "ds", "us", "sw", "gr", "gr", "gr", "gr"},
    {"gr", "gr", "gr", "gr", "ob", "ds", "us", "sw", "gr", "gr", "de", "dw", "sw", "ds", "us", "sw", "dw", "ho", "gr", "gr", "sw", "ds", "us", "sw", "gr", "gr", "ho", "gr", "sw", "ds", "us", "sw", "dw", "ho", "gr", "gr"},
    {"ho", "gr", "ho", "gr", "sw", "ds", "us", "sw", "dw", "de", "gr", "gr", "sw", "ds", "us", "sw", "gr", "gr", "ho", "gr", "ob", "ds", "us", "sw", "dw", "ho", "dw", "gr", "sw", "ds", "us", "sw", "gr", "gr", "ho", "gr"},
    {"dw", "gr", "dw", "gr", "sw", "ds", "us", "sw", "gr", "gr", "gr", "gr", "sw", "ds", "us", "sw", "gr", "gr", "dw", "gr", "sw", "ds", "us", "sw", "gr", "gr", "dw", "gr", "sw", "ds", "us", "sw", "gr", "gr", "dw", "gr"},
    {"sw", "sw", "sw", "sw", "sw", "cw", "cw", "sw", "ob", "sw", "sw", "sw", "sw", "cw", "cw", "sw", "sw", "sw", "sw", "sw", "sw", "cw", "cw", "sw", "ob", "sw", "ob", "sw", "sw", "cw", "cw", "sw", "ob", "sw", "sw", "sw"},
    {"ls", "ls", "ls", "ls", "cw", "ic", "ic", "cw", "ls", "ls", "ls", "ls", "cw", "ic", "ic", "cw", "ls", "ls", "ls", "ls", "cw", "ic", "ic", "cw", "ls", "ls", "ls", "ls", "cw", "ic", "ic", "cw", "ls", "ls", "ls", "ls"},
    {"rs", "rs", "rs", "rs", "cw", "ic", "ic", "cw", "rs", "rs", "rs", "rs", "cw", "ic", "ic", "cw", "rs", "rs", "rs", "rs", "cw", "ic", "ic", "cw", "rs", "rs", "rs", "rs", "cw", "ic", "ic", "cw", "rs", "rs", "rs", "rs"},
    {"sw", "sw", "sw", "sw", "sw", "cw", "cw", "sw", "sw", "sw", "sw", "sw", "sw", "cw", "cw", "sw", "sw", "sw", "sw", "sw", "sw", "cw", "cw", "sw", "sw", "sw", "sw", "sw", "sw", "cw", "cw", "sw", "sw", "sw", "sw", "sw"},
    {"gr", "dw", "gr", "gr", "sw", "ds", "us", "sw", "gr", "gr", "gr", "gr", "sw", "ds", "us", "sw", "gr", "gr", "ho", "dw", "sw", "ds", "us", "sw", "gr", "gr", "gr", "gr", "sw", "ds", "us", "sw", "gr", "dw", "gr", "gr"},
    {"gr", "ho", "gr", "gr", "sw", "ds", "us", "sw", "gr", "gr", "ho", "dw", "sw", "ds", "us", "ob", "dw", "de", "gr", "gr", "sw", "ds", "us", "sw", "dw", "ho", "ho", "dw", "ob", "ds", "us", "sw", "gr", "de", "gr", "gr"},
    {"gr", "gr", "de", "dw", "sw", "ds", "us", "sw", "dw", "ho", "gr", "gr", "ob", "ds", "us", "sw", "gr", "gr", "gr", "gr", "sw", "ds", "us", "sw", "gr", "gr", "gr", "gr", "sw", "ds", "us", "sw", "ob", "gr", "gr", "gr"},
    {"gr", "gr", "gr", "gr", "sw", "ds", "us", "sw", "gr", "gr", "ho", "dw", "sw", "ds", "us", "sw", "gr", "gr", "gr", "gr", "ob", "ds", "us", "sw", "dw", "ho", "ho", "dw", "sw", "ds", "us", "sw", "dw", "ho", "gr", "gr"}
    };




    private void Start()
    {

    }
   

    public void UpdateAgents(Dictionary<int, MobileAgentData> agentData)
    {
        foreach (var agent in agentData)
        {
            int id = agent.Key;
            MobileAgentData data = agent.Value;

            if (data.type == "CarAgent")
            {
                if (!carAgents.ContainsKey(id))
                {
                    AddAgent(data, carPrefab, id);
                }
                else
                {
                    UpdatePosition(carAgents[id], data, carPrefab, id);
                }
            }
            else if (data.type == "PedestrianAgent")
            {
                if (!pedestrianAgents.ContainsKey(id))
                {
                    AddAgent(data, pedestrianPrefab, id);
                }
                else
                {
                    UpdatePosition(pedestrianAgents[id], data, pedestrianPrefab, id);
                }
            }
            
        }
    }

    private void AddAgent(MobileAgentData data, GameObject prefab, int id)
    {
        Vector3 position = new Vector3(data.x, data.y, data.z);
        GameObject newAgent = Instantiate(prefab, position, Quaternion.identity);
        newAgent.name = $"Agent {data.type} {data.x}, {data.y}, {data.z}";
        if (data.type == "CarAgent")
        {
            string roadType = GetRoadType((int)data.x, (int)data.z);
            Quaternion orientation = GetOrientation(roadType);
            newAgent.transform.rotation = orientation;
            carAgents[id] = newAgent;
        }
        else if (data.type == "PedestrianAgent")
        {
            pedestrianAgents[id] = newAgent;
        }
    }

    private void UpdatePosition(GameObject agent, MobileAgentData data, GameObject prefab, int id)
    {
        // GameObject agentObject = cars[carId];
        Vector3 currentPosition = agent.transform.position;
        Vector3 targetPosition = new Vector3(data.x, data.y, data.z);
        Quaternion currentRotation = agent.transform.rotation;

        if ((data.x == 0 && currentPosition.x == 11) || (data.x == 11 && currentPosition.x == 0) || (data.z == 0 && currentPosition.z == 35) || (data.z == 35 && currentPosition.z == 0))
        {
            Destroy(agent);
            GameObject newAgent = Instantiate(prefab, targetPosition, Quaternion.identity);
            newAgent.name = $"Agent {data.type} {data.x}, {data.y}, {data.z}";
            newAgent.transform.rotation = currentRotation;
            if (data.type == "CarAgent")
            {
                carAgents[id] = newAgent;
            }
            else if (data.type == "PedestrianAgent")
            {
                pedestrianAgents[id] = newAgent;
            }
        }
        else 
        {
            StartCoroutine(MoveAgentToPosition(agent, targetPosition));
            // StartCoroutine(MoveCarToPosition(cars[carId], targetPosition));
        }
    }

    private string GetRoadType(int x, int z)
    {
        if (x >= 0 && x < roadMap.GetLength(0) && z >= 0 && z < roadMap.GetLength(1))
        {
            return roadMap[x, z];
        }
        return "gr"; // Default to grass
    }

    private Quaternion GetOrientation(string roadType)
    {
        switch (roadType)
        {
            case "ls": return Quaternion.Euler(0, 180, 0);
            case "rs": return Quaternion.Euler(0, 0, 0);
            case "ds": return Quaternion.Euler(0, 90, 0);
            case "us": return Quaternion.Euler(0, -90, 0);
            default: return Quaternion.identity;
        }
    }

   private System.Collections.IEnumerator MoveAgentToPosition(GameObject car, Vector3 targetPosition)
{
    while (Vector3.Distance(car.transform.position, targetPosition) > 0.01f)
    {
        Vector3 direction = targetPosition - car.transform.position;
        if (direction != Vector3.zero)
        {
            // Rotate the car smoothly toward the target position
            Quaternion targetRotation = Quaternion.LookRotation(direction);
            car.transform.rotation = Quaternion.Slerp(car.transform.rotation, targetRotation, rotationSpeed);
        }

        // Move the car toward the target position
        car.transform.position = Vector3.MoveTowards(car.transform.position, targetPosition, moveSpeed * Time.deltaTime);

        yield return null; // Wait for the next frame
    }
    car.transform.position = targetPosition;
}
 
}
