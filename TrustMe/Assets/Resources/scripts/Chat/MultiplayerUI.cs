using System.Collections;
using System.Collections.Generic;
using UnityEngine;
using Unity.Netcode;
using UnityEngine.UI;

public class MultiplayerUI : MonoBehaviour
{
    [SerializeField] Button hostBtn, joinBtn;
    [SerializeField] Animator fadeLobbyscreen;
    public Animator fadeLobbyscreenAnimator { get { return fadeLobbyscreen; } }
    private int resStateParaHash = 0;

    void Awake()
    {
        resStateParaHash = Animator.StringToHash("inState");
        AssignInputs();
    }


    // Update is called once per frame
    void AssignInputs()
    {
        hostBtn.onClick.AddListener(delegate { 
            NetworkManager.Singleton.StartHost();
            fadeLobbyscreenAnimator.SetInteger(resStateParaHash, 1);

            // Buttons nach der Animation deaktivieren (sie werden nicht mehr sichtbar oder interaktiv sein)
            hostBtn.gameObject.SetActive(false);
            joinBtn.gameObject.SetActive(false);

            StartCoroutine(WaitForFadeToEnd());
        });
        joinBtn.onClick.AddListener(delegate { 
            NetworkManager.Singleton.StartClient();
            fadeLobbyscreenAnimator.SetInteger(resStateParaHash, 1);

            // Buttons nach der Animation deaktivieren (sie werden nicht mehr sichtbar oder interaktiv sein)
            hostBtn.gameObject.SetActive(false);
            joinBtn.gameObject.SetActive(false);

            StartCoroutine(WaitForFadeToEnd());
        });

    }

    // Coroutine, um die Animation abzuwarten und den Zustand zu ändern
    IEnumerator WaitForFadeToEnd()
    {
        // Warte, bis die Animation beendet ist (Anpassung des Namens je nach deiner Animation)
        yield return new WaitForSeconds(fadeLobbyscreenAnimator.GetCurrentAnimatorStateInfo(0).length);

        // Zustand auf 2 setzen, um den finalen Zustand festzuhalten
        fadeLobbyscreenAnimator.SetInteger(resStateParaHash, 2);
    }
}