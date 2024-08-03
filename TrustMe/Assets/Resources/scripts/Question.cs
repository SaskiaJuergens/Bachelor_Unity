using System.Collections;
using System.Collections.Generic;
using UnityEngine;

[System.Serializable]
public struct Answer
{
    [SerializeField] private string _info;
    public string Info {  get { return _info;  } }
    [SerializeField] private bool _isCorrect;
    public bool IsCorret { get { return _isCorrect; } }
}

[CreateAssetMenu(fileName = "New Question", menuName = "Quiz/new Questions")]
public class Question : ScriptableObject
{
    public enum AnswerType { Multi, Single }

    // The Serializedfields will be visible in the Inspector,
    // but they remain private and are not accessible from other scripts.
    [SerializeField] private string _info = string.Empty;
    public string Info { get { return _info; } }

    [SerializeField] Answer[] _answers = null; //Array
    public Answer[] Answers {  get { return _answers; } }

    //Parameters
    [SerializeField] private bool _userTimer = false;
    public bool UserTimer { get { return _userTimer; } }

    [SerializeField] private int _timer = 0;
        public int Timer { get { return _timer; } }

    [SerializeField] private AnswerType _answerType = AnswerType.Multi;
    public AnswerType GetAnswerType { get { return _answerType; } }

    [SerializeField] private int _addScore = 10;
    public int AddScore {  get { return _addScore; } }

    public List<int> GetCorrektAnswers()
    {
        List<int> CorrectAnswers = new List<int>();
        for (int i = 0; i < Answers.Length; i++)
        {
            if (Answers[i].IsCorret)
            {
                CorrectAnswers.Add(i);
            }
        }
        return CorrectAnswers;
    }

}
