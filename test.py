import dash
import dash_core_components as dcc
import dash_html_components as html
from pymongo import MongoClient
from collections import Counter

client = MongoClient()
db = client['snitch-db']
fixVersions = db.fixVersions
allFixVersionChanges = fixVersions.find()
fixVersionDatesInQa = []
fixVersionDatesNotInQa = []
fixVersionIssueKeysInQa = []
fixVersionIssueKeysNotInQa = []
fixVersionPointLabelsInQa = []
fixVersionPointLabelsNotInQa = []
usersForCount = []
users = []
fixVersionChangesPerUser = []


def add_fix_version_point(fix_version_dates, fix_version_issue_keys, fix_version_point_labels, change):
    fix_version_dates.append(change['timestamp'])
    fix_version_issue_keys.append(change['issueKey'][0:3])
    fix_version_point_labels.append(change['issueKey'] + ' : ' + change['user'])


for change in allFixVersionChanges:
    usersForCount.append(change['user'])
    if change['userIsInQa']:
        add_fix_version_point(fixVersionDatesInQa, fixVersionIssueKeysInQa, fixVersionPointLabelsInQa, change)
    else:
        add_fix_version_point(fixVersionDatesNotInQa, fixVersionIssueKeysNotInQa, fixVersionPointLabelsNotInQa, change)

for user, count in Counter(usersForCount).items():
    users.append(user)
    fixVersionChangesPerUser.append(count)

app = dash.Dash()

app.layout = html.Div(children=[
    html.H1(children='Fix Version Stats'),

    dcc.Graph(
        id='main',
        figure={
            'data': [
                {
                    'x': fixVersionDatesInQa,
                    'y': fixVersionIssueKeysInQa,
                    'text': fixVersionPointLabelsInQa,
                    'type': 'scatter',
                    'mode': 'markers',
                },
                {
                    'x': fixVersionDatesNotInQa,
                    'y': fixVersionIssueKeysNotInQa,
                    'text': fixVersionPointLabelsNotInQa,
                    'type': 'scatter',
                    'mode': 'markers',
                    'marker': {
                        'size': 5,
                        'color': 'rgba(255, 182, 193, .9)',
                    }
                }
            ],
            'layout': {
                'title': 'Fix Version Changes Timeline'
            }
        }
    ),

    dcc.Graph(
        id='secondary',
        figure={
            'data': [
                {
                    'x': users,
                    'y': fixVersionChangesPerUser,
                    'type': 'bar'
                }
            ],
            'layout': {
                'title': '# of Fix Version Changes By User'
            }
        }
    )
])

if __name__ == '__main__':
    app.run_server(debug=True)