import logging
import datetime
import os

def getLogger(*args,**kwargs):
    '''
    custom method allowing us to create a fileloghandler and a consolehandler.
    print the information on console and writing in log file.
    :param name: logger need have a name!
    :param log_level: the logger level { CRITICAL | ERROR | WAENING | INFO | DEBUG }

    '''
    try:
        log_level = kwargs['log_level']
    except KeyError:
        log_level = logging.ERROR
        
    try:
        logger_name = kwargs['name']
    except KeyError:
        logger_name = 'XAOLogger'
    try:
        log_text = kwargs['text']
    except KeyError:
        log_text = 'test!'
       
    logger = logging.getLogger(logger_name)
    
    if logger.handlers:
        return False,logger
    else:
        filename = '{}.log'.format(logger_name)
        file_handler = logging.FileHandler(filename)
        file_handler = logging.FileHandler(filename)
        formatted_datetime = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S.%f')[:-4]
        formatted_string = formatted_datetime+' %(name)s:'  + ':%(levelname)s:' \
                        ':%(filename)s:%(lineno)d - %(msg)s'
        file_handler.setFormatter(logging.Formatter(formatted_string))
        logger.addHandler(file_handler)
        
        console_handler = logging.StreamHandler()
        logger.addHandler(console_handler)        
    logger.setLevel(log_level)
    return True,logger
    

    
    
    
    