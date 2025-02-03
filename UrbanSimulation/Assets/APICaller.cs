using System.Collections;
using UnityEngine;
using UnityEngine.Networking;

public class APICaller : MonoBehaviour
{
    private string baseUrl = "http://127.0.0.1:5000";
    private string mobileRequest = "/simulation_stats";
    private float interval = 5.0f;

    // Start is called once before the first execution of Update after the MonoBehaviour is created
    void Start()
    {
        StartCoroutine(CallAPI());       
    }

    private IEnumerator CallAPI() 
    {
        for (int i = 0; i < 10; i++)
        {
            yield return StartCoroutine(GetRequest());
            yield return new WaitForSeconds(interval);
        }
    }

    private IEnumerator GetRequest()
    {
        string url = baseUrl + mobileRequest;
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
            }
        }
    }
}