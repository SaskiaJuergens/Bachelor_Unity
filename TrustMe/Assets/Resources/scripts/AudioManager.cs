using System.Collections;
using System.Collections.Generic;
using UnityEngine;


[System.Serializable()]
public struct SoundParameters
{
    [Range(0, 1)]
    public float Volume;
    [Range(-3, 3)]
    public float Pitch;
    public bool Loop;
}
[System.Serializable()]
public class Sound
{
    #region Variables

    [SerializeField] string name;
    public string Name { get { return name; } }

    [SerializeField] AudioClip clip = null;
    public AudioClip Clip { get { return clip; } }

    [SerializeField] SoundParameters parameters = new SoundParameters();
    public SoundParameters Parameters { get { return parameters; } }

    [HideInInspector]
    public AudioSource Source = null;

    #endregion

    public void Play()
    {
        Source.clip = Clip;

        Source.volume = Parameters.Volume;
        Source.pitch = Parameters.Pitch;
        Source.loop = Parameters.Loop;

        Source.Play();
    }
    public void Stop()
    {
        Source.Stop();
    }
}

public class AudioManager : MonoBehaviour
{
    #region Variables

    public static AudioManager Instance = null;

    [SerializeField] Sound[] sounds;
    [SerializeField] AudioSource sourcePrefab;

    [SerializeField] string startupTrack;

    #endregion

    void Awake()
    {
        if (Instance != null)
        { Destroy(gameObject); }
        else
        {
            Instance = this;
            DontDestroyOnLoad(gameObject);
        }
        InitSound();

    }

    void Start()
    {
        // Function that is called when the script instance is being loaded.
        if (string.IsNullOrEmpty(startupTrack) != true)
        {
            playSound(startupTrack);
        }
    }

    void InitSound()
    {
        foreach (var sound in sounds)
        {
            AudioSource scource = (AudioSource)Instantiate(sourcePrefab, gameObject.transform);
            scource.name = sound.Name;

            sound.Source = scource;
        }
    }

    public void playSound(string name)
    {
        var sound = GetSound(name);
        if(sound != null)
        {
            sound.Play();
        }
        else
        {
            Debug.LogWarning("Sound by the name " + name + " is not found! Issue occured at AudioManager Play()");
        }
    }
    public void stopSound(string name) 
    {
        var sound = GetSound(name);
        if(sound != null)
        {
            sound.Stop();
        }
        else
        {
            Debug.LogWarning("Sound by the name " + name + " is not found! Issue occured at AudioManager Stop()");
        }
    }
    Sound GetSound (string name)
    {
        foreach(var sound in sounds)
        {
            if(sound.Name == name)
            {
                return sound;
            }
        }
        return null;
    }
}

