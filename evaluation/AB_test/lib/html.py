import os
import lib.ir


def html(name):
    with open(os.path.join('lib','html',name), 'r') as f:
        return f.read()



def page(body):
    return "".join([
        html('head.html'),
        html('header.html'),
        body,
        html('footer.html')
        ])



def html_starvote(doc_id):
    return '<div class="starvote">%s</div>'%(
        ''.join(['<img src="https://upload.wikimedia.org/wikipedia/commons/d/df/Star_icon_1.png" alt="%d" />'%(i) for i in range(5)]
                )
        )

def html_results(query):
    results = lib.ir.search(query)
    body_lines = []
    for i, (c_name, c_body) in enumerate(results):
        body_lines.append('<dt>{i}. {n}{stars}</dt><dd>{b}</dd>'.format(
            i=i+1, n=c_name, b=c_body, stars=html_starvote(c_name)))
    return "".join(body_lines)
