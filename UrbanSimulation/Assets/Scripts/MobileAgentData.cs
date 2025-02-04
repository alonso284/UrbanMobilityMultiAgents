using UnityEngine;

[System.Serializable]
    public class MobileAgentData
    {
        public string type;
        public int x;
        public int y;
        public int z;

        public MobileAgentData(string type, int x, int y, int z = 0)
        {
            this.type = type;
            this.x = x;
            this.y = z;
            this.z = y;
        }
    }
