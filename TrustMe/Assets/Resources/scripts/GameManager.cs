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

    //Timer
    [SerializeField] Animator TimerAnimator = null;
    [SerializeField] TextMeshProUGUI timerText = null;
    [SerializeField] Color timerHalfOutColor = Color.yellow;
    [SerializeField] Color timerAlmostOutColor = Color.red;
    private Color TimeDefaultColor = Color.white;

    private List<AnswerData> PickedAnswers = new List<AnswerData>();
    private List<int> finishedQuestions = new List<int>();
    private int currentQuestion = 0;
    //private int score;
    private IEnumerator IE_WaitTillNextRound = null;
    private IEnumerator IE_StartTimer = null;

    //getter if finished the Game
    private bool gameFinished
    {
        get
        {
            return (finishedQuestions.Count < Questions.Length) ? false : true;
        }
    }

    /// Function that is called when the object becomes enabled and active
    void OnEnable()
    {
        events.UpdateQuestionAnswer += UpdateAnswer;
    }
    /// Function that is called when the behaviour becomes disabled
    void OnDisable()
    {
        events.UpdateQuestionAnswer -= UpdateAnswer;
    }
    /// Function that is called on the frame when a script is enabled just before any of the Update methods are called the first time.
    void Awake()
    {
        //events.CurrentFinalScore = 0;
    }

    private void Start()
    {
        TimeDefaultColor = timerText.color;
        
        LoadQuestions();


        //random qustion wird ausgesucht
        //var seed = UnityEngine.Random.Range(int.MinValue, int.MaxValue);
        //UnityEngine.Random.InitState(seed);

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

        if (events.UpdateQuestionUI != null)
        {
            events.UpdateQuestionUI(question);
        }
        else { Debug.LogWarning("Ups! Something went wrong while trying to display new Question UI Data. GameEvents.UpdateQuestionUI is null. Issue occured in GameManager.Display() method."); }

        //if (question.UseTimer)
        //{
            //UpdateTimer(question.UseTimer);
        //}

    }

    public void Accept()
    {
        //UpdateTimer(false);
        bool isCorrect = checkAnswer();
        finishedQuestions.Add(currentQuestion);

        UpdateScore((isCorrect) ? Questions[currentQuestion].AddScore : -Questions[currentQuestion].AddScore);

        if (gameFinished)
        {
            //SetHighscore();
        }

        var type
            = (gameFinished)
            ? UIManager.ResolutionScreenType.Finish
            : (isCorrect) ? UIManager.ResolutionScreenType.Correct
            : UIManager.ResolutionScreenType.Incorrect;


        if (events.DisplayResolutionScreen != null) 
        {
            events.DisplayResolutionScreen(type, Questions[currentQuestion].AddScore);

        }

        //AudioManager.Instance.PlaySound((isCorrect) ? "CorrectSFX" : "IncorrectSFX");

        if (type != UIManager.ResolutionScreenType.Finish)
        {
            if (IE_WaitTillNextRound != null)
            {
                StopCoroutine(IE_WaitTillNextRound);
            }
            IE_WaitTillNextRound = WaitTillNextRound();
            StartCoroutine(IE_WaitTillNextRound);
        }

    }


    void UpdateTimer(bool state)
    {
        switch (state)
        {
            case true:
                IE_StartTimer = StartTimer();
                StartCoroutine(IE_StartTimer);
                break;

            case false:
                if(IE_StartTimer != null)
                {
                    StopCoroutine(IE_StartTimer);
                }
                break;
        }
    }

    IEnumerator StartTimer()
    {
        var totalTime = Questions[currentQuestion].Timer;
        var timeLeft = totalTime;

        timerText.color = TimeDefaultColor;
        while (timeLeft > 0)
        {
            timeLeft--;
            if (timeLeft < totalTime / 2 && timeLeft > totalTime / 4)
            {
                timerText.color = timerHalfOutColor;
            }
            if (timeLeft < totalTime / 4)
            {
                timerText.color = timerAlmostOutColor;
            }
            timerText.text = timeLeft.ToString();
            yield return new WaitForSeconds(1.0f);
        }
        Accept();
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
