using UnityEngine;

[System.Serializable]
    public class StaticAgentData 
    {
        public bool status;
        public int x;
        public int y;
        public int z;

        public StaticAgentData(bool status, int x, int y, int z = 1)
        {
            this.status = status;
            this.x = x;
            this.y = z;
            this.z = y;
        }
    }
