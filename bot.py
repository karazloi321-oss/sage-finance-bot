from flask import Flask
import os

app = Flask(**name**)

@app.route("/")
def home():
return """ <html> <head> <title>Sage Finance</title> <meta name="viewport" content="width=device-width, initial-scale=1"> <style>
body{
background:#d9e5d6;
font-family:sans-serif;
padding:40px;
text-align:center;
}

```
        .card{
            background:white;
            padding:30px;
            border-radius:20px;
            max-width:400px;
            margin:auto;
        }

        h1{
            color:#1f2a1f;
        }

        button{
            width:100%;
            padding:18px;
            border:none;
            border-radius:16px;
            background:#7c9b76;
            color:white;
            font-size:20px;
            margin-top:20px;
        }
    </style>
</head>

<body>

    <div class="card">

        <h1>Sage Finance</h1>

        <h2>Баланс: 0 ₽</h2>

        <button>
            Добавить расход
        </button>

    </div>

</body>
</html>
"""
```

if **name** == "**main**":
app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 10000)))

