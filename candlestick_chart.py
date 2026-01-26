from streamlit_echarts import st_echarts

def candlestick_chart_display (datelist, ohlclist):
    option = {
                "tooltip": {
                                "trigger": 'axis'
                            },
                "toolbox": {
                            "feature": {
                            "dataZoom": {
                                "yAxisIndex": "true"
                            },
                            "brush": {
                                "type": ['lineX', 'clear']
                            }
                            }
                        },
                "xAxis": {
                    "data": datelist
                },
                "yAxis": {"scale": "false"},
                "series": [
                    {
                    "type": 'candlestick',
                    "data": ohlclist
                    }
                ]
                }
    return(option)