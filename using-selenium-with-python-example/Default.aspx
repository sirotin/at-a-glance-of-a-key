<%@ Page Language="C#" AutoEventWireup="true" CodeFile="Default.aspx.cs" Inherits="_Default" %>

<!DOCTYPE html>

<html xmlns="http://www.w3.org/1999/xhtml">
<head runat="server">
    <title>Simple web-page demonstration - Using cookies</title>
    <style type="text/css">
        html, body {
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
        }
        td {
            text-align: center;
            height: 40px;
        }
        #table-container-1 {
            width: 100%;
            height: 100%;
            display: table;
            margin-top: 100px;
        }
        #table-container-2 {
            vertical-align: middle;
            display: table-cell;
            height: 100%;
        }
        #my-table {
            margin: 0 auto;
            width: 400px;
            border: 1px solid;
            padding: 10px;
        }
        td.left-cell {
            width: 150px;
        }
        td.right-cell {
            width: 300px;
        }
        #cookie_value {
            width: 220px;
        }
        #form_submit {
            width: 100px;
        }
    </style>
</head>
<body>
    <form id="cookie_updater_form" method="post" runat="server">
        <div id="table-container-1"><div id="table-container-2">
            <table id="my-table">
                <tr>
                    <td class="left-cell">Current Value:</td>
                    <td class="right-cell" id="current_cookie" runat="server"></td>
                </tr>
                <tr>
                    <td class="left-cell">New Value:</td>
                    <td class="right-cell"><input id="cookie_value" type="text" maxlength="15" runat="server"/></td>
                </tr>
                <tr>
                    <td colspan="2"><input id="form_submit" type="submit" runat="server"/></td>
                </tr>
            </table>
        </div></div>
    </form>
</body>
</html>
