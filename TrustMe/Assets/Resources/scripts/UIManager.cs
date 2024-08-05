using System;
using System.Collections;
using System.Collections.Generic;
using TMPro;
using UnityEngine;
using UnityEngine.UI;

[Serializable()]
public struct UIManagerParameters
{
    [Header("Answers Options")]
    [SerializeField] float margins;
    public float Margins { get { return margins; } }

    [Header("Resolution Screen Options")]
    [SerializeField] Color correctBGColor;
    public Color CorrectBGColor { get { return correctBGColor; } }
    [SerializeField] Color incorrectBGColor;
    public Color IncorrectBGColor { get { return incorrectBGColor; } }
    [SerializeField] Color finalBGColor;
    public Color FinalBGColor { get { return finalBGColor; } }
}

[Serializable()]
public struct UIElements
{
    [SerializeField] RectTransform answerContentArea;
    public RectTransform AnswerContentArea { get { return answerContentArea; } }

    [SerializeField] TextMeshProUGUI questionInfoTextObj;
    public TextMeshProUGUI QuestionInfoTextObj { get { return questionInfoTextObj; } }

    [SerializeField] TextMeshProUGUI scoreText;
    public TextMeshProUGUI ScoreText { get { return scoreText; } }

    [Space]

    [SerializeField] Animator resolutionScreenAnimator;
    public Animator ResolutionScreenAnimator { get { return resolutionScreenAnimator; } }

    [SerializeField] Image resolutionBG;
    public Image ResolutionBG { get { return resolutionBG; } }

    [SerializeField] TextMeshProUGUI resolutionStateInfoText;
    public TextMeshProUGUI ResolutionStateInfoText { get { return resolutionStateInfoText; } }

    [SerializeField] TextMeshProUGUI resolutionScoreText;
    public TextMeshProUGUI ResolutionScoreText { get { return resolutionScoreText; } }

    [Space]

    [SerializeField] TextMeshProUGUI highScoreText;
    public TextMeshProUGUI HighScoreText { get { return highScoreText; } }

    [SerializeField] CanvasGroup mainCanvasGroup;
    public CanvasGroup MainCanvasGroup { get { return mainCanvasGroup; } }

    [SerializeField] RectTransform finishUIElements;
    public RectTransform FinishUIElements { get { return finishUIElements; } }
}


public class UIManager : MonoBehaviour
{
    public enum ResolutionScreenType { Correct, Incorrect, Finish }

    [Header("References")]
    [SerializeField] GameEvents events;

    [Header("UI Elemts (Prefabs)")]
    [SerializeField] AnswerData answerPrefab;

    [SerializeField] UIElements uIElements;

    [Space]
    [SerializeField] UIManagerParameters parameters;

    List<AnswerData> currentAnswers = new List<AnswerData>();

    private void OnEnable()
    {
        if (events == null)
        {
            Debug.LogError("GameEvents not assigned in the UIManager.");
            return;
        }

        events.UpdateQuestionUI += UpdateQuestionsUI;
    }
    private void OnDisable()
    {
        if (events != null)
        {
            events.UpdateQuestionUI -= UpdateQuestionsUI;
        }
    }
    void UpdateQuestionsUI(Question question)
    {
        uIElements.QuestionInfoTextObj.text = question.Info;
        CreateAnswers(question);
    }

    void CreateAnswers (Question question)
    {
        EraseAnswers();

        float offset = 0 - parameters.Margins;
        for (int i= 0; i < question.Answers.Length; i++)
        {
            AnswerData newAnswer = (AnswerData)Instantiate(answerPrefab, uIElements.AnswerContentArea);
            newAnswer.UpdateData(question.Answers[i].Info, i);

            newAnswer.Rect.anchoredPosition = new Vector2(0, offset);

            offset -= (newAnswer.Rect.sizeDelta.y + parameters.Margins);
            uIElements.AnswerContentArea.sizeDelta = new Vector2(uIElements.AnswerContentArea.sizeDelta.x, offset * -1);

            currentAnswers.Add(newAnswer);
        }
    }

    void EraseAnswers()
    {
        foreach (var answer in currentAnswers)
        {
            Destroy(answer.gameObject);
        }
        currentAnswers.Clear();
    }
}
