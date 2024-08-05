using System.Collections;
using System.Collections.Generic;
using System.Linq;
using TMPro;
using UnityEngine;
using UnityEngine.SceneManagement;

public class GameManager : MonoBehaviour
{
    Question[] _questions = null;
    public Question[] Questions { get { return _questions; } }

    [SerializeField] GameEvents events = null;

    private List<AnswerData> PickedAnswers = new List<AnswerData>();
    private List<int> finishedQuestions = new List<int>();
    private int currentQuestion = 0;
    //private int score;

    private void Start()
    {
        if (events == null)
        {
            Debug.LogError("GameEvents not assigned in the GameManager.");
            return;
        }

        LoadQuestions();

        if (_questions == null || _questions.Length == 0)
        {
            Debug.LogError("No questions loaded. Please check the Resources/Questions folder.");
            return;
        }

        foreach (var question in Questions)
        {
            if (question != null)
            {
                Debug.Log(question.Info);
            }
            else
            {
                Debug.LogError("Null question found in the Questions array.");
            }
        }
        Display();
    }

    public void EraseAnswers()
    {
        PickedAnswers = new List<AnswerData>();
    }

    void Display()
    {
        EraseAnswers();
        var question = GetRandomQuestion();

        if (question == null)
        {
            Debug.LogError("No question available to display.");
            return;
        }

        if (events != null && events.UpdateQuestionUI != null)
        {
            events.UpdateQuestionUI(question);
        }
        else
        {
            Debug.LogWarning("Something went wrong while trying to display new Question UI Data. GameEvents.UpdateQuestionUI is null. Issues occurred in GameManager.Display() method");
        }

    }

    Question GetRandomQuestion()
    {
        var randomIndex = GetRandomQuestionIndex();
        currentQuestion = randomIndex;

        return Questions[currentQuestion];
    }

    int GetRandomQuestionIndex()
    {
        var random = 0;
        if (finishedQuestions.Count < Questions.Length)
        {
            do
            {
                random = UnityEngine.Random.Range(0, Questions.Length);
            } while (finishedQuestions.Contains(random) || random == currentQuestion);
        }
        return random;
    }

    void LoadQuestions()
    {
        Object[] objs = Resources.LoadAll("Questions", typeof(Question));
        _questions = new Question[objs.Length];
        for (int i = 0; i < objs.Length; i++)
        {
            _questions[i] = (Question)objs[i];
        }
    }


}
