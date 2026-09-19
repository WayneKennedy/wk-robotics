#!/usr/bin/env bash
# Enrol several head poses of one person without watching a screen: tones on the machine
# running this script say when to move and when the sample was taken.
#
#   enrol_poses.sh <bench-host> <name> [pose ...]      default poses: left right down up
#
# Per pose:  one long low tone  = move to the next pose and hold it
#            (capture ~7 s later: HOLD_S, then ~5 s for ros2 topic pub over ssh; the next
#            frame's largest face is saved)
#            two rising beeps   = captured, relax
#            one low buzz       = no face saved within 10 s; the pose is retried (3 tries)
# Finish:    three rising beeps.
#
# Runs where the speaker is, talks to the bench host over ssh; the bench must be running
# (~/hailo/bench.sh on the host). Env: AUDIO_DEV (ALSA device, default "default"),
# PLAY (player, default "aplay -q"; e.g. "sudo -n aplay -q" if the user is not in the
# audio group), HOLD_S (seconds between the move tone and sending the enrol command, default 2).
set -euo pipefail
host=${1:?usage: enrol_poses.sh <bench-host> <name> [pose ...]}
name=${2:?usage: enrol_poses.sh <bench-host> <name> [pose ...]}
shift 2
poses=("$@"); [ ${#poses[@]} -gt 0 ] || poses=(left right down up)
dev=${AUDIO_DEV:-default}; play=${PLAY:-aplay -q}; hold=${HOLD_S:-2}
tmp=$(mktemp -d); trap 'rm -rf "$tmp"' EXIT

# tone <file> <freq:seconds> ... — sine tones separated by 80 ms of silence
tone() {
  local out=$1; shift
  python3 - "$out" "$@" <<'EOF'
import math, struct, sys, wave
r = 44100; frames = b""
for spec in sys.argv[2:]:
    f, d = map(float, spec.split(":"))
    n = int(r * d)
    frames += b"".join(struct.pack("<h", int(18000 * math.sin(2 * math.pi * f * i / r) * min(1, i / 400, (n - i) / 400))) for i in range(n))
    frames += b"\0\0" * int(r * 0.08)
w = wave.open(sys.argv[1], "wb"); w.setnchannels(1); w.setsampwidth(2); w.setframerate(r); w.writeframes(frames); w.close()
EOF
}
tone "$tmp/move.wav" 440:0.7
tone "$tmp/ok.wav" 880:0.15 1320:0.2
tone "$tmp/miss.wav" 180:0.8
tone "$tmp/done.wav" 660:0.15 880:0.15 1320:0.3
beep() { $play -D "$dev" "$tmp/$1.wav"; }

remote() { ssh -o BatchMode=yes "$host" "$@"; }
enrolled_count() { remote "grep -c \"enrolled '$name'\" ~/hailo/bench.log || true"; }
publish() {  # $1 = name, or "" to cancel a pending enrol
  remote "source /opt/ros/jazzy/setup.bash && ros2 topic pub --once -w 1 /hailo/enroll std_msgs/msg/String '{data: \"$1\"}' >/dev/null"
}

for pose in "${poses[@]}"; do
  for try in 1 2 3; do
    echo "pose '$pose', try $try: move and hold"
    beep move; sleep "$hold"
    before=$(enrolled_count)
    publish "$name"
    ok=0
    for _ in $(seq 20); do
      [ "$(enrolled_count)" -gt "$before" ] && { ok=1; break; }
      sleep 0.5
    done
    if [ $ok = 1 ]; then
      remote "grep \"enrolled '$name'\" ~/hailo/bench.log | tail -1 | sed 's/.*]: //'"
      beep ok; sleep 2; break
    fi
    publish ""  # cancel, so a later face is not saved under this name
    echo "  no face saved"; beep miss; sleep 2
  done
done
beep done
echo "done; restart the bench only if gallery files were edited by hand (enrolments load live)"
