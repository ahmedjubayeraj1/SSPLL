# source tools/env.sh   - set the PDK and tool paths for this repo
# Edit PDK_ROOT if your PDK lives elsewhere. Inside IIC-OSIC-TOOLS these are already set.
export PDK_ROOT=${PDK_ROOT:-$HOME/pdk}
export PDK=${PDK:-sky130A}
export SSPLL_ROOT=$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)
[ -d /home/claude/eda/bin ] && export PATH=/home/claude/eda/bin:$PATH
