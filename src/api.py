# Copyright (C) 2023 KNOWRON GmbH <ask@knowron.com>
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <https://www.gnu.org/licenses/>.
#
# For license information on the libraries used, see LICENSE.

"""Route definitions."""

from fastapi import APIRouter
from fastapi.responses import HTMLResponse

from src.extract.views import router as extract_router

# v1 routes
api_router_v1 = APIRouter()
api_router_v1.include_router(extract_router, prefix="/extract", tags=["extract"])

# Root routes
api_router_root = APIRouter()


@api_router_root.get("/", response_class=HTMLResponse, status_code=200)
def read_root():
    logo_html = """
   `/.   :fm@Zni.<br>
 :LWMRL_~FY;uQMM@J.<br>
/@MMMMMWeae. cMMMM%:     TQl :LD5`  TQX"  iQL   :LNXZXNT;  IQn  sQN' .NO. ~QD8SZXn   .oXNZ%NZt   "QQ5.  PQ<br>
XMMMMMMMQ; .. 8MMMM6     dM]}DZ/    dMPKt tMk  .OQs   |Q@: :W@..XEQo sMn  /Mm   8M)  8Mu.  :%M[  "ME@U- ZM<br>
MMMMMMMMM[iQD_uMMMMO     dMW@QP:    dMioQaiMk  !MN     ZMt  TMsDiegoM8Q"  /MWUSm@L  .RQ_    }MC  "MZ"OX;ZM<br>
mMMMMMMMQ; _: 8MMMM6     dMT.!NN!   dMi ?WPMk  .XQl   |Q@:  /QFXF !QTQ8   /MX:\KX"   qM5.  :ZMj  "MZ -S@mM<br>
/@MMMMMQf[s. cMMMM%:     kQc  :ZW[  TQi  /NQL   :LNXZmNT_    SQQ!  YQQ    /Q%  ~N@|  .yXNZ%NZt   "QQ   nQQ<br>
 :LWMWk;!ZS;uQMM@J.<br>
   '\`   :xm@Zni.<br>
    """.strip().replace(" ", "&nbsp;")

    return f"""
        <!DOCTYPE html>
        <html lang="en">
        <head>
            <meta charset="utf-8">
            <title>KNOWRON FOSS API</title>
        </head>
        <body>
            <p style="font-family:'Lucida Console', monospace">{logo_html}</p>
        </body>
        </html>
    """


@api_router_root.get("/healthcheck", status_code=200)
def healthcheck():
    return {"status": "ok"}
