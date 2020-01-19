using System.Collections;
using System.Collections.Generic;
using UnityEngine;

public class SphereColiderPoints : MonoBehaviour
{
    public Player player;
    public GameObject sphere;
    private void OnTriggerEnter(Collider other)
    {
        player.score += 1;
        if (player.fuel <= 75)
        {
            player.fuel += 25;
        }
        else
        {
            player.fuel = 100;
        }
        sphere.SetActive(false);
        player.spawnedPoint = false;

    }
}
