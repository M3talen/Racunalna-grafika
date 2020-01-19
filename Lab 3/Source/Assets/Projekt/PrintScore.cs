using System.Collections;
using System.Collections.Generic;
using UnityEngine;
using UnityEngine.UI;

public class PrintScore : MonoBehaviour
{
    public Text txt;
    public Player player;

    void Update()
    {
        string fuelString = "";
        int fuelBig = player.fuel / 10;
        for (int i = 0; i < 10; i++)
        {
            if (fuelBig != 0)
            {
                fuelString += '█';
                fuelBig -= 1;
            }
            else
            {
                fuelString += '░';
            }
        }
        txt.text = "SCORE : " + player.score + "\n FUEL : " + fuelString;
    }
}
