using UnityEngine;
using System.Collections;
using System.Collections.Generic;
using UnityEngine.Networking;
using Newtonsoft.Json;

public class APICaller : MonoBehaviour
{
    private const string BASE_URL = "http://127.0.0.1:5000";
    private const string MOBILE_REQUEST_PATH = "/mobile_agent_state/";
    private const string STATIC_REQUEST_PATH = "/static_agent_state/";
    private const float INTERVAL = 0.4f;
    private const int STEPS = 60;

    public AgentController agentController;
    public StaticAgentController staticAgentController;

    void Start()
    {
        StartCoroutine(CallAPI());
    }

    private IEnumerator CallAPI()
    {
        for (int step = 1; step < STEPS; step++)
        {
            Debug.Log($"Step: {step}");
            string urlMobile = BASE_URL + MOBILE_REQUEST_PATH + step;
            string urlStatic = BASE_URL + STATIC_REQUEST_PATH + step;
            yield return StartCoroutine(GetRequest(step, urlStatic, true));
            yield return StartCoroutine(GetRequest(step, urlMobile, false));
            yield return new WaitForSeconds(INTERVAL);
        }
    }

    private IEnumerator GetRequest(int step, string url, bool staticAgent)
    {
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
                string jsonResponse = request.downloadHandler.text;
                if (staticAgent)
                {
                    ParseAndUpdateStaticAgents(jsonResponse);
                }
                else
                {
                    ParseAndUpdateMobileAgents(jsonResponse);
                }
            }
        }
    }


    void ParseAndUpdateMobileAgents(string jsonResponse)
    {

        List<MobileDataEntry> rawData = JsonConvert.DeserializeObject<List<MobileDataEntry>>(jsonResponse);

        Dictionary<int, MobileAgentData> agentData = new Dictionary<int, MobileAgentData>();
        Dictionary<int, MobileAgentData> pedestrianData = new Dictionary<int, MobileAgentData>();
        foreach (var item in rawData)
        {
            agentData[item.id] = new MobileAgentData(item.type, item.x, item.y);
        }
        
        agentController.UpdateAgents(agentData);

    }

    void ParseAndUpdateStaticAgents(string jsonResponse)
    {
        List<StaticDataEntry> rawData = JsonConvert.DeserializeObject<List<StaticDataEntry>>(jsonResponse);

        Dictionary<int, StaticAgentData> agentData = new Dictionary<int, StaticAgentData>();
        foreach (var item in rawData)
        {
            agentData[item.id] = new StaticAgentData(item.status, item.x, item.y);
        }
        
        staticAgentController.UpdateStaticAgents(agentData);
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

[System.Serializable]
public class StaticDataEntry
{
    public int id;
    public bool status;
    public int x;
    public int y;
}