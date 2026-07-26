**Tier 1: You can measure these today, no users needed at all**

These are pure engineering metrics, you just run the system and log the numbers yourself.

- Latensi end to end: add a timestamp right when audio input starts and right when TTS audio starts playing back. Run it 10 to 20 times and average it.
- Frame rate: most browsers have a built in FPS counter (Chrome DevTools performance tab), or you can log `requestAnimationFrame` timestamps in Three.js.
- Akurasi transkripsi Whisper: record yourself or teammates reading 15 to 20 short scripted answers, run them through Whisper, and compare the output text to what was actually said (word error rate).
- RAM usage: just watch server memory while a session runs, no special tooling required.
- Sinkronisasi gerak bibir: this one's a bit more manual, you'd compare the timestamp of a viseme trigger against the corresponding audio waveform peak.

None of this needs a stranger sitting in front of your app. Your own team is a perfectly valid tester for engineering metrics.

**Tier 2: Needs a handful of people, but they don't have to be your real target audience**

This covers the functional metrics for Dynamic Stress Interview and Persona Shift.

- Write a small script of test candidate answers on purpose: some vague, some contradictory, some confident. Run each through the system and check whether the model actually escalates the way it's supposed to.
- Have two or three teammates or friends role play as candidates for five to ten minutes each, just to see if Persona Shift triggers consistently.

This is closer to internal QA testing than user research, so classmates or teammates are fine here too.

**Tier 3: This is the one that actually needs outside people, UEQ-S and PRCS-B**

This is the part you're missing, and it's fair to be a little worried about it since it's the only tier where "no users" is a real gap. But a few things worth knowing:

- You don't need real job seekers or Akmil applicants specifically. A convenience sample, classmates, friends, dorm mates works fine for a competition stage paper, as long as you're honest in the paper that it's a pilot test with a small non representative sample.
- Ten people is genuinely a small ask. If you can get even five to seven friends to each do a 10 to 15 minute session before the deadline, that's enough for a legitimate "preliminary result" section, even if it's not your final claimed number.
- PRCS-B before and after just needs two short questionnaires, one right before the session, one right after. You could literally send it as a Google Form.

**My honest suggestion on priority, given limited time before the demo**

1. Do Tier 1 first, since it costs you nothing but a few hours and gives you real numbers to replace the "target" language in the paper.
2. Do Tier 2 next, since it validates that your two headline features actually work as claimed, which matters more for judges than the UX numbers.
3. Try to squeeze in even a small Tier 3 pilot, five people is far better than zero. If you truly can't get anyone in time, it's more honest to keep the current phrasing ("evaluasi dirancang, hasil belum tersedia") than to fabricate numbers.

If it'd help, I can also help you draft the actual test script for the candidate role play scenarios, or the two short questionnaire forms for UEQ-S and PRCS-B, just say which one you want first.
