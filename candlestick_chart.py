from streamlit_echarts import st_echarts

def candlestick_chart_display(datelist, ohlclist):
    option = {
        "backgroundColor": "#FFFFFF",  # Sets background to absolute white
        "tooltip": {
            "trigger": 'axis',
            "axisPointer": {"type": 'cross'}
        },
        "xAxis": {
            "type": 'category',
            "data": datelist,
            "scale": True,
            "boundaryGap": False,
            "axisLine": {"show": False},      # Removes the X-axis line
            "splitLine": {"show": False}      # Removes vertical grid lines
        },
        "yAxis": {
            "scale": True,
            "axisLine": {"show": False},      # Removes the Y-axis line
            "splitLine": {"show": False}      # Removes horizontal grid lines
        },
        "dataZoom": [
            {
                "type": 'inside',
                "start": 50,
                "end": 100
            },
            {
                "show": True,
                "type": 'slider',
                "top": '90%',
                "start": 50,
                "end": 100
            }
        ],
        "series": [
            {
                "type": 'candlestick',
                "data": ohlclist,
                "itemStyle": {
                    "color": "#089981",       # Green for Bullish
                    "color0": "#f23645",      # Red for Bearish
                    "borderColor": "#089981", # Matches border to fill
                    "borderColor0": "#f23645" # Matches border to fill
                }
            }
        ]
    }
    return option

# def candlestick_chart_display(datelist, ohlclist):
#     option = {
#         "tooltip": {
#             "trigger": 'axis',
#             "axisPointer": {"type": 'cross'}
#         },
#         "toolbox": {
#             "feature": {
#                 "dataZoom": {"yAxisIndex": "none"},
#                 "restore": {},
#                 "saveAsImage": {}
#             }
#         },
#         "xAxis": {
#             "type": 'category',
#             "data": datelist,
#             "scale": True,
#             "boundaryGap": False,
#         },
#         "yAxis": {
#             "scale": True, # Very important: prevents the Y-axis from starting at 0
#             "splitArea": {"show": True}
#         },
#         "dataZoom": [
#             {
#                 "type": 'inside', # This enables mouse-wheel zooming and touch-drag scrolling
#                 "start": 50,      # Initial zoom level (shows last 50% of data)
#                 "end": 100
#             },
#             {
#                 "show": True,     # This adds the scrollbar slider at the bottom
#                 "type": 'slider',
#                 "top": '90%',
#                 "start": 50,
#                 "end": 100
#             }
#         ],
#         "series": [
#             {
#                 "type": 'candlestick',
#                 "data": ohlclist,
#                 "itemStyle": {
#                     "color": "#ec0000",   # Bullish (NSE red/green is usually reversed globally)
#                     "color0": "#00da3c",  # Bearish
#                     "borderColor": "#8A0000",
#                     "borderColor0": "#008F28"
#                 }
#             }
#         ]
#     }
#     return option

