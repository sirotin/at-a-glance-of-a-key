// Author: Alexander Sirotin / sirotin@gmail.com
// Copyright (c) 2017 Alexander Sirotin.
// Licensed under MIT license:
// https://opensource.org/licenses/mit-license.php
// Your use is on an "AS-IS" basis, and subject to the terms and conditions of this license.

using System;
using System.Text;
using System.Web;

public partial class _Default : System.Web.UI.Page
{
    protected void Page_Load(object sender, EventArgs e)
    {
        // In case of form post, update cookie
        var post = Request.Form["cookie_value"];
        if (post != null) {
            var newCookie = new HttpCookie("demo");
            newCookie.Value = Convert.ToBase64String(Encoding.UTF8.GetBytes(post));
            newCookie.Expires = DateTime.Now.AddMinutes(10);

            Response.Cookies.Remove("demo");
            Response.Cookies.Add(newCookie);

            // Update current display
            Request.Cookies.Set(newCookie);
        }

        // Read current cookie value
        var cookie = Request.Cookies["demo"];
        if (cookie == null) {
            current_cookie.InnerText = "Cookie does not exist!";
        }
        else {
            current_cookie.InnerText = Encoding.UTF8.GetString(Convert.FromBase64String(cookie.Value));
        }
    }
}
