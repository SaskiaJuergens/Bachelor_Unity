using System.Collections;
using System.Collections.Generic;
using UnityEngine;
using TMPro;

public class ChatMessanger : MonoBehaviour
{
    [SerializeField] TextMeshProUGUI messageText;

    public void SetText(string message)
    {
        messageText.text = message;
    }
}
