using System.Collections;
using System.Collections.Generic;
using TMPro;
using UnityEngine;
using UnityEngine.UI;

public class AnswerData : MonoBehaviour
{
    [Header("UI Elements")]
    [SerializeField] TextMeshProUGUI infoTextObject;
    [SerializeField] Image toggle;

    [Header("Textures")]
    [SerializeField] Sprite uncheckedToggle;
    [SerializeField] Sprite checkedToggle;

    private int _answerIndex = -1;
    public int AnswerIndex { get { return _answerIndex; } }

}
