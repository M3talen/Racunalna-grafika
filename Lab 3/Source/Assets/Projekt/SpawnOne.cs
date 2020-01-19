using System;
using System.Collections.Generic;
using UnityEngine;

public class SpawnOne : MonoBehaviour
{
    public Player player;
    public List<GameObject> spawns;

    private void Start()
    {
        spawns[0].SetActive(true);
        player.spawnedPoint = true;
    }

    void Update()
    {
        if (!player.spawnedPoint)
        {
            var random = new System.Random();
            int index = random.Next(spawns.Count);
            spawns[index].SetActive(true);
            player.spawnedPoint = true;
        }
        
    }
}
