using System.Collections;
using System.Collections.Generic;
using System.Linq;
using TMPro;
using UnityEngine;
using UnityEngine.SceneManagement;

public class GameManager : MonoBehaviour
{
    private Question[] _questions = null;
    public Question[] Questions { get { return _questions; } }

    [SerializeField] GameEvents events = null;

    private List<AnswerData> PickedAnswers = new List<AnswerData>();
    private List<int> finishedQuestions = new List<int>();
    private int currentQuestion = 0;
    //private int score;
    private IEnumerator IE_WaitTillNextRound = null;


    private void Start()
    {
        //random qustion wird ausgesucht
        //var seed = UnityEngine.Random.Range(int.MinValue, int.MaxValue);
        //UnityEngine.Random.InitState(seed);

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

    /// Function that is called to update new selected answer.
    public void UpdateAnswer(AnswerData newAnswer)
    {
        if (Questions[currentQuestion].GetAnswerType == Question.AnswerType.Single)
        {
            foreach (var answer in PickedAnswers)
            {
                if (answer != newAnswer)
                {
                    answer.Reset();
                }
            }
            PickedAnswers.Clear();
            PickedAnswers.Add(newAnswer);
        }
        else
        {
            bool alreadyPicked = PickedAnswers.Exists(x => x == newAnswer);
            if (alreadyPicked)
            {
                PickedAnswers.Remove(newAnswer);
            }
            else
            {
                PickedAnswers.Add(newAnswer);
            }
        }
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

    public void Accept()
    {
        bool isCorrect = checkAnswer();
        finishedQuestions.Add(currentQuestion);

        UpdateScore((isCorrect) ? Questions[currentQuestion].AddScore : -Questions[currentQuestion].AddScore);
        
        if (IE_WaitTillNextRound != null)
        {
            StopCoroutine(IE_WaitTillNextRound);
        }
        IE_WaitTillNextRound = WaitTillNextRound();
        StartCoroutine(IE_WaitTillNextRound);
    
    }

    IEnumerator WaitTillNextRound()
    {
        yield return new WaitForSeconds(GameUtility.ResolutionDelayTime);
        Display();
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

    /// Function that is called to check currently picked answers and return the result.
    bool checkAnswer()
    {
        if (!CompareAnswers())
        {
            return false;
        }
        return true;
    }
    bool CompareAnswers()
    {
        if (PickedAnswers.Count > 0)
        {
            //List of correct Answres c
            List<int> c = Questions[currentQuestion].GetCorrectAnswers();
            //List of picked Ansers p
            List<int> p = PickedAnswers.Select(x => x.AnswerIndex).ToList();

            var f = c.Except(p).ToList();
            var s = p.Except(c).ToList();

            return !f.Any() && !s.Any();
        }
        return false;
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

    /// Function that updates the score and update the UI.
    private void UpdateScore(int add)
    {
        events.CurrentFinalScore += add;

        if (events.ScoreUpdated != null)
        {
            events.ScoreUpdated();
        }
    }


}
