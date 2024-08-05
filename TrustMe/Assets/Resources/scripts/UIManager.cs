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
    [SerializeField] float topMargin; // Abstand vom oberen Rand des Containers zur ersten Antwort
    [SerializeField] float answerSpacing; // Abstand zwischen Antworten
    public float TopMargin { get { return topMargin; } }
    public float AnswerSpacing { get { return answerSpacing; } }

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

    void CreateAnswers(Question question)
    {
        EraseAnswers();

        // Initial offset to start placing answers from the top
        float offset = -parameters.TopMargin;

        // Clear existing answers list
        currentAnswers.Clear();

        // Initialize height of the AnswerContentArea
        float contentHeight = 0;

        for (int i = 0; i < question.Answers.Length; i++)
        {
            // Instantiate a new answer prefab
            AnswerData newAnswer = Instantiate(answerPrefab, uIElements.AnswerContentArea);

            // Update the data of the new answer
            newAnswer.UpdateData(question.Answers[i].Info, i);

            // Set the position of the new answer
            newAnswer.Rect.anchoredPosition = new Vector2(0, offset);

            // Update offset for the next answer
            offset -= (newAnswer.Rect.rect.height + parameters.AnswerSpacing);

            // Increment the contentHeight for the current answer
            contentHeight += (newAnswer.Rect.rect.height + parameters.AnswerSpacing);

            // Add the new answer to the list of current answers
            currentAnswers.Add(newAnswer);
        }

        // Ensure the contentHeight does not exceed maxContentHeight
        contentHeight = Mathf.Min(contentHeight, 5);

        // Adjust the content area size to fit all answers but not exceed maxContentHeight
        uIElements.AnswerContentArea.sizeDelta = new Vector2(uIElements.AnswerContentArea.sizeDelta.x, contentHeight);
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
