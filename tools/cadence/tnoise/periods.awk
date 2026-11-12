# periods.awk - period statistics of vop-vom from a Spectre psfascii transient (rising zero crossings, t > 30 ns)
/^"time"/ { t = $2; next }
/^"vop"/  { vp = $2; next }
/^"vom"/  { vd = vp - $2
            if (have && vdp < 0 && vd >= 0 && t > 30e-9) {
                tc = tp + (0 - vdp) * (t - tp) / (vd - vdp)
                if (lastc > 0) { n++; per[n] = tc - lastc }
                lastc = tc }
            vdp = vd; tp = t; have = 1; next }
END { if (n < 2) { print "no periods found"; exit }
      for (i = 1; i <= n; i++) s += per[i]; m = s / n
      for (i = 1; i <= n; i++) ss += (per[i] - m)^2
      printf "periods %d   mean %.5f ps (f = %.5f GHz)   period jitter %.1f fs rms\n", n, m*1e12, 1e-9/m, sqrt(ss/(n-1))*1e15 }
