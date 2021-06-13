# Copyright (C) 2020-2021 by DevsExpo@Github, < https://github.com/DevsExpo >.
#
# This file is part of < https://github.com/DevsExpo/FridayUserBot > project,
# and is released under the "GNU v3.0 License Agreement".
# Please see < https://github.com/DevsExpo/blob/master/LICENSE >
#
# All rights reserved.

import asyncio
import io
import sys
import traceback

import requests

from main_startup.core.decorators import friday_on_cmd
from main_startup.core.startup_helpers import run_cmd
from main_startup.helper_func.basic_helpers import (
    edit_or_reply,
    edit_or_send_as_file,
    get_text,
)


EVAL = "**▶ Code :** \n`{code}` \n\n**▶ Output / TraceBack :** \n`{result}`"


@friday_on_cmd(
    cmd=["exec", "eval"],
    ignore_errors=True,
    cmd_help={"help": "Run Python Code!", "example": '{ch}eval print("FridayUserBot")'},
)
async def eval(client, message):
    engine = message.Engine
    stark = await edit_or_reply(message, engine.get_string("PROCESSING"))
    cmd = get_text(message)
    if not cmd:
        await stark.edit(engine.get_string("INPUT_REQ").format("Chat ID"))
        return
    if message.reply_to_message:
        message.reply_to_message.message_id
    old_stderr = sys.stderr
    old_stdout = sys.stdout
    redirected_output = sys.stdout = io.StringIO()
    redirected_error = sys.stderr = io.StringIO()
    stdout, stderr, exc = None, None, None
    try:
        await aexec(cmd, client, message)
    except Exception:
        exc = traceback.format_exc()
    stdout = redirected_output.getvalue()
    stderr = redirected_error.getvalue()
    sys.stdout = old_stdout
    sys.stderr = old_stderr
    evaluation = ""
    if exc:
        evaluation = exc
    elif stderr:
        evaluation = stderr
    elif stdout:
        evaluation = stdout
    else:
        evaluation = "Success!"
    final_output = EVAL.format(code=cmd, result=evaluation)
    if len(cmd) >= 1023:
        capt = "Eval Result!"
    else:
        capt = cmd
    await edit_or_send_as_file(final_output, stark, client, capt, "eval-result")


async def aexec(code, client, message):
    exec(
        f"async def __aexec(client, message): "
        + "".join(f"\n {l}" for l in code.split("\n"))
    )
    return await locals()["__aexec"](client, message)


@friday_on_cmd(
    cmd=["rc", "run"],
    cmd_help={
        "help": "Reply To Any Programming Language's Code To Eval In Telegram!",
        "example": "{ch}run python print('FridayUserBot')",
    },
)
async def any_lang_cmd_runner(client, message):
    engine = message.Engine
    stark = await edit_or_reply(message, engine.get_string("PROCESSING"))
    if len(message.text.split()) == 1:
        await stark.edit(engine.get_string("INPUT_REQ").format("Chat ID"))
        return
    if not message.reply_to_message:
        await stark.edit(engine.get_string("REPLY_CODE"))
        return
    reply_code = message.reply_to_message.text
    lang = message.text.split(None, 1)[1]
    if not lang.lower() in langs:
        await stark.edit(engine.get_string("INVALID_RC_LANG"))
        return
    if reply_code is None:
        await stark.edit(engine.get_string("REPLY_CODE"))
        return
    data = {
        "code": reply_code,
        "lang": lang,
        "token": "5b5f0ad8-705a-4118-87d4-c0ca29939aed",
    }
    r = requests.post("https://starkapis.herokuapp.com/compiler", data=data).json()
    if r.get("reason") != None:
        iujwal = f"""**▶ Code :** \n`{reply_code}` 
**▶ Result :** 
`{r.get("results")}`
**▶ Error :** 
`{r.get("errors")}`
**▶ Stats :**
 `{r.get("stats")}`
**▶ Success :** 
 `{r.get("success")}`
**▶ Warnings :** 
 `{r.get("warnings")}`
**▶ Reason :**
 `{r.get("reason")}`
 """
    else:
        iujwal = f"""**▶ Code :** \n`{reply_code}` 
**▶ Result :** 
`{r.get("results")}`
**▶ Error :** 
`{r.get("errors")}`
**▶ Stats :**
 `{r.get("stats")}`
**▶ Success :** 
 `{r.get("success")}`
**▶ Warnings :** 
 `{r.get("warnings")}`
 """
    await edit_or_send_as_file(
        iujwal, stark, client, "`Result of Your Code!`", "rc-result"
    )


@friday_on_cmd(
    cmd=["bash", "terminal"],
    ignore_errors=True,
    cmd_help={"help": "Run Bash/Terminal Command!", "example": "{ch}bash ls"},
)
async def sed_terminal(client, message):
    engine = message.Engine
    stark = await edit_or_reply(message, engine.get_string("WAIT"))
    cmd = get_text(message)
    if not cmd:
        await stark.edit(engine.get_string("INPUT_REQ").format("Chat ID"))
        return
    cmd = message.text.split(None, 1)[1]
    if message.reply_to_message:
        message.reply_to_message.message_id

    pid, err, out, ret = await run_command(cmd)
    if not out:
        out = "No OutPut!"
    friday = f"""**▶ CMD :**
`{cmd}`

**▶ PID :**
`{pid}`

**▶ Error TraceBack (If Any) :**
`{err}`

**▶ Output / Result (If Any) :**
`{out}`

**▶ Return Code :** 
`{ret}`
"""
    await edit_or_send_as_file(friday, stark, client, cmd, "bash-result")


async def run_command(cmd):
    process = await asyncio.create_subprocess_shell(
        cmd, stdout=asyncio.subprocess.PIPE, stderr=asyncio.subprocess.PIPE
    )
    stdout, stderr = await process.communicate()
    errors = stderr.decode()
    if not errors:
        errors = "No Errors!"
    output = stdout.decode()
    return process.pid, errors, output, process.returncode
