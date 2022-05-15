from flask import Flask, render_template, request
from datetime import datetime
import mpld3
import backtrader as bt
import yfinance as yf
import matplotlib.pyplot as plt
from matplotlib import warnings
app=Flask(__name__)

class BuyAndHold_Buy(bt.Strategy):
    def start(self):
        self.val_start = self.broker.get_cash()  # keep the starting cash

    def nextstart(self):
        # Buy stocks with all the available cash
        size = int(self.val_start / self.data)
        self.buy(size=size)

    def stop(self):
        # calculate the actual returns
        self.roi = ((self.broker.get_value() / self.val_start) - 1.0)*100
        self.cash = self.broker.get_value()
        print("ROI: %.2f, Cash: %.2f" % (self.roi, self.cash))

@app.route('/')
def hello_world():
    return render_template('index.html')

@app.route('/result', methods=['POST', 'GET'])
def result():
    stock=request.form['stock']
    startdate=request.form['startdate']
    enddate=request.form['enddate']
    startdate : datetime.strptime(startdate,'%Y-%m-%d')
    enddate : datetime.strptime(startdate,'%Y-%m-%d')
    try:
        data = bt.feeds.PandasData(dataname=yf.download(stock, startdate, enddate))
    except Exception as e:
        return render_template('index.html', error="The mentioned date is not valid"), 400
    cerebro = bt.Cerebro()
    cerebro.adddata(data)
    cerebro.addstrategy(BuyAndHold_Buy, "HODL")
    cerebro.run()
    finalportfoliovalue=cerebro.broker.getvalue()
    pt=cerebro.plot(iplot=False)
    return render_template('result/html', stock=stock, cost_val=finalportfoliovalue, fig=pt)

@app.errorhandler(500)
def id_not_found(e):
    stock=request.form['stock']
    ename = str(stock)
    return render_template('index.html', error="The given Stock: {} is not valid".format(ename)), 500


@app.errorhandler(400)
def err1found(e):
    return render_template('index.html', error="ERROR: Please Try Again "), 400


@app.errorhandler(404)
def err2found(e):
    return render_template('index.html', error="ERROR: Please Try Again "), 404


@app.errorhandler(403)
def err3found(e):
    return render_template('index.html', error="ERROR: Please Try Again "), 403


if __name__ == '__main__':
    app.run(debug=True)

