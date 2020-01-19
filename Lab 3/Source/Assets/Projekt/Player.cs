using UnityEngine;
public class Player : MonoBehaviour
{
    public int score;
    public int fuel = 100;
    public bool spawnedPoint = false;
    public Player()
    {
    }

    public void Update()
    {
        if (fuel <= 0)
        {
            score = 0;
            fuel = 100;
        }
    }

    private void Awake()
    {
        InvokeRepeating("DecreaseFuel", 2.0f, 0.75f);
    }

    void DecreaseFuel()
    {
        fuel -= 1;
    }
}
