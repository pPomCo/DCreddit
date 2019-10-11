from flask import Flask
app = Flask(__name__)


from lib.html import *


@app.route('/')
def index():
    body = """
  <form action="#" onsubmit="window.location.href='/'+forms[0].user_name.value+'/'+forms[0].profile.value+'/'; return false;">
    <table>
      <tr>
        <td>Your name: </td>
        <td><input type="text" name="user_name" value="no-name" /></td>
      </tr>
      <tr>
        <td>Select your profile:</td>
        <td>
          <select name="profile">
            <option value="no-profile">No profile</option>
            <option value="politics">Politics</option>
          </select>
        </td>
      </tr>
      <tr>
        <td colspan="2">
          <input type="submit" value="Start"  />
        </td>
      </tr>
    </table>
  </form>
"""
    return page(body)


@app.route('/<user_name>/<profile>/')
def query(user_name, profile):
    body = """
  <p>
    Hello dear {uname} (profile='{uprof}'). <br/>
    Please <strong>query our system</strong> to find Reddit comments
  </p>
  <div class="searchbar">
    <form onsubmit="window.location.href='/{uname}/{uprof}/'+forms[0].query.value; return false;">
      <input type="text" name="query" placeholder="Query..." />
      <input type="submit" value="Search"  />
    </form>
  </div>
""".format(uname=user_name, uprof=profile)
    return page(body)


@app.route('/<user_name>/<profile>/<query>')
def results(user_name, profile, query):
    body = """
  <p>
    Hello dear {uname} (profile='{uprof}'). <br />
    Please <strong>give a score</strong> to the returned Reddit comments
  </p>
  <p>
    Query: <em>{q}</em>
  </p>
  <dl>{results}</dl>
  <div class="next_action">
    <p>Next action:</p>
    <ul>
      <li><a href="/{uname}/{uprof}">Continue querying</a></li>
      <li><a href="/">Change user</a></li>
    </ul>
  </div>
""".format(uname=user_name, uprof=profile, q=query, results=html_results(query))
    return page(body)
