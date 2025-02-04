using System.Collections.Generic;
using UnityEngine;
using System.IO;

public class PedestrianAgent : MonoBehaviour
{
    public GameObject pedestrianPrefab;

    private Dictionary<int, GameObject> pedestrians = new Dictionary<int, GameObject>();

    public float moveSpeed = 5.0f;

    // Start is called once before the first execution of Update after the MonoBehaviour is created
    void Start()
    {
        
    }

    // Update is called once per frame
    public void UpdatePedestrians(Dictionary<int, MobileAgentData> pedestrianData)
    {
        foreach (var pedestrian in pedestrianData)
        {
            int pedestrianId = pedestrian.Key;
            MobileAgentData data = pedestrian.Value;

            if (!pedestrians.ContainsKey(pedestrianId))
            {
                Vector3 startPosition = new Vector3(data.x, data.y, data.z);
                GameObject newPedestrian = Instantiate(pedestrianPrefab, startPosition, Quaternion.identity);
                newPedestrian.name = $"Pedestrian {pedestrianId}";

                pedestrians[pedestrianId] = newPedestrian;
            }
            else 
            {
             StartCoroutine(MovePedestrian(pedestrianId, data));   
            }
        }
    }
    

    private System.Collections.IEnumerator MovePedestrian(int pedestrianId, MobileAgentData data)
    {
        GameObject pedestrian = pedestrians[pedestrianId];
        Vector3 targetPosition = new Vector3(data.x, data.y, data.z);
        while (pedestrian.transform.position != targetPosition)
        {
            pedestrian.transform.position = Vector3.MoveTowards(pedestrian.transform.position, targetPosition, moveSpeed * Time.deltaTime);
            yield return null;
        }
    }
}
