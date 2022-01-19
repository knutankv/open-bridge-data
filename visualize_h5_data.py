from opyndata import interface

data_path = 'C:/Users/knutankv/BergsoysundData/data_10Hz.h5'
app_setup = interface.AppSetup(data_path=data_path)
app = app_setup.create_app()

server = app.server
    
# ------------ RUN SERVER -------------
if __name__ == '__main__':
    app.run_server(debug=False)