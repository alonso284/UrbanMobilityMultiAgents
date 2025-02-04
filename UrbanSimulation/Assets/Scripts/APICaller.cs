using UnityEngine;
using System.Collections;
using System.Collections.Generic;
using UnityEngine.Networking;
using Newtonsoft.Json;

public class APICaller : MonoBehaviour
{
    private string baseUrl = "http://127.0.0.1:5000";
    private string mobileRequest = "/mobile_agent_state/";
    private float interval = 0.5f;

    private int STEPS = 60;

    public AgentController agentController;

    void Start()
    {
        StartCoroutine(CallAPI());
    }

    private IEnumerator CallAPI()
    {
        for (int i = 1; i < STEPS; i++)
        {
            yield return StartCoroutine(GetRequest(i));
            yield return new WaitForSeconds(interval);
        }
    }

    private IEnumerator GetRequest(int step)
    {
        string url = baseUrl + mobileRequest + step;
        Debug.Log($"Requesting: {url}");
        using (UnityWebRequest request = UnityWebRequest.Get(url))
        {
            yield return request.SendWebRequest();

            if (request.result != UnityWebRequest.Result.Success)
            {
                Debug.LogError(request.error);
            }
            else
            {
                Debug.Log($"Response: {request.downloadHandler.text}");
                string jsonResponse = request.downloadHandler.text;
                ParseAndUpdate(jsonResponse);
            }
        }
    }


    void ParseAndUpdate(string jsonResponse)
    {

        List<MobileDataEntry> rawData = JsonConvert.DeserializeObject<List<MobileDataEntry>>(jsonResponse);

        Dictionary<int, MobileAgentData> agentData = new Dictionary<int, MobileAgentData>();
        Dictionary<int, MobileAgentData> pedestrianData = new Dictionary<int, MobileAgentData>();
        foreach (var item in rawData)
        {
            agentData[item.id] = new MobileAgentData(item.type, item.x, item.y);
            
            // Debug.Log($"Agent ID: {item.id}, Position: {item.x}, {item.y}");
        }
        
        agentController.UpdateAgents(agentData);

    }

}

[System.Serializable]
public class MobileDataEntry
{
    public int id;
    public int x;
    public int y;
    public string type;
}