#Requires AutoHotkey v2.0

#HotIf WinActive("SQL Server Management Studio")
^+x::  ; Ctrl+shift+X
{
    ; send Ctlr+shift+C
    Send("^+c")
    Sleep(100)
    ClipWait
    text := A_Clipboard
    lines := StrSplit(text, "`n", "`r")
    header := lines.RemoveAt(1)

    unique := Map()
    result := []
    for val in lines {
        val := Trim(val)
        if (val = "")
            continue
        if !unique.Has(val) {
            unique[val] := true
            if (val = "NULL")
                result.Push("NULL")
            else
                result.Push("N'" val "'")
        }
    }
    

    formatted := header " IN (" StrJoin(result, ", ") ")"
    A_Clipboard := formatted
}
#HotIf

StrJoin(arr, sep := ", ") {
    result := ""
    for i, v in arr
        result .= (i > 1 ? sep : "") v
    return result
}