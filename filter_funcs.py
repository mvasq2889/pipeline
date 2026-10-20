from antares_devkit.models import BaseFilter
from antares_devkit.models import DevKitLocus
from antares_client import search
import numpy as np
import matplotlib.pyplot as plt
from astropy.time import Time
import pandas as pd
import math
from astropy.coordinates import Angle, SkyCoord
import astropy.units as u
import time
import warnings
import itertools
import pdb
from astropy.io import fits

#LSST
#qualtiy check
def lsst_quality(alert):
    quality = True
    quality &= alert.properties['lsst_diaSource_reliability'] >= 0.6
    quality &= alert.properties['lsst_diaSource_psfFlux_flag'] == False
    quality &= alert.properties['lsst_diaSource_centroid_flag'] == False
    quality &= alert.properties['lsst_diaSource_shape_flag'] == False
    quality &= alert.properties['lsst_diaSource_isDipole'] == False
    quality &= alert.properties['lsst_diaSource_pixelFlags_saturated'] == False
    quality &= alert.properties['lsst_diaSource_pixelFlags_edge'] == False
    quality &= alert.properties['lsst_diaSource_pixelFlags_cr'] == False
    quality &= alert.properties['lsst_diaSource_pixelFlags_streak'] == False
    quality &= alert.properties['lsst_diaSource_scienceFlux'] >= 0
    quality &= alert.properties['lsst_diaSource_templateFlux'] >= 0

    if 'lsst_diaSource_ssObjectId' in alert.properties:
        quality &= alert.properties['lsst_diaSource_ssObjectId'] in (0, None, "0")
    return quality
    
#extract data
def lsst_alert(alert):
    obs_date = float(alert.properties['lsst_diaSource_midpointMjdTai'])
    oid_mag = float(-2.5*np.log10(alert.properties['lsst_diaSource_scienceFlux']) + 31.4)
    temp_mag = float(-2.5*np.log10(alert.properties['lsst_diaSource_templateFlux']) + 31.4)
    diff_mag = float(temp_mag - oid_mag)
    
    bandpass = alert.properties['lsst_diaSource_band']
    band = 'lsst_' + str(bandpass)

    if alert.properties['lsst_diaSource_isNegative'] == True:
        pos_or_neg = -1
    else:
        pos_or_neg = 1
        
    return {band: [obs_date, oid_mag, temp_mag, diff_mag, pos_or_neg]}

#ZTF
#quality check
def ztf_quality(alert):
    quality = True
    quality &= alert.properties['ztf_rb'] >= 0.65
    quality &= alert.properties['ztf_nbad'] == 0
    quality &= alert.properties['ztf_fwhm'] <= 5
    quality &= alert.properties['ztf_elong'] <= 1.2
    quality &= abs(alert.properties['ztf_magdiff']) <= 1.
    return quality

#extract data
#uses formula from 260609 6/15 markdown cell
def ztf_alert(alert):
    bands = ['x', 'g', 'R', 'i']
    
    band_id = alert.properties['ztf_fid']
    obs_date = float(alert.properties['ant_mjd'])
    ant_mag = alert.properties['ant_mag']
    temp_mag = alert.properties['ztf_magnr']
    temp_mag_err = alert.properties['ztf_sigmagnr']
    diff_img_mag = alert.properties['ztf_magpsf']
    diff_img_mag_err = alert.properties['ztf_sigmapsf']
    
    if alert.properties['ztf_isdiffpos'] == 'f' or alert.properties['ztf_isdiffpos'] == 0:
        pos_or_neg = -1
        m =  (1 - 10.**(0.4*(temp_mag - diff_img_mag)))
    else:
        pos_or_neg = 1
        m = (10.**(0.4*(temp_mag - diff_img_mag)) + 1)

    if m <= 0.01:
        diff_mag = 10**(-10)
    else:
        diff_mag = -2.5* np.log10(m)
    oid_mag = diff_mag + temp_mag
    band = 'ztf_' + str(bands[band_id])
    data = {'mjd': obs_date, 'band': band, 'm_sci': oid_mag, 'm_template': temp_mag, 'm_diff': diff_img_mag, 
            'delta_m': diff_mag, 'pos_or_neg': pos_or_neg}
    return data

#extract data
#error propagation
def ztf_alert_err(alert):
    bands = ['x', 'g', 'R', 'i']
    band_id = alert.properties['ztf_fid']
    obs_date = float(alert.properties['ant_mjd'])
    ant_mag = alert.properties['ant_mag']
    temp_mag = alert.properties['ztf_magnr']
    temp_mag_err = alert.properties['ztf_sigmagnr']
    diff_img_mag = alert.properties['ztf_magpsf']
    diff_img_mag_err = alert.properties['ztf_sigmapsf']
    n = 10.**(0.4*(temp_mag - diff_img_mag))
    flag = 0
    
    if alert.properties['ztf_isdiffpos'] == 'f' or alert.properties['ztf_isdiffpos'] == 0:
        pos_or_neg = -1
        if 1-n <= 0.:
            diff_mag = 10**(-10)
            oid_mag_err = np.sqrt( 2**2 *temp_mag_err**2 + diff_img_mag_err**2 )
            flag = 1
        else:
            diff_mag = -2.5* np.log10(1-n)
            oid_mag_err = np.sqrt( (1+n/(1-n))**2 * temp_mag_err**2 + (-n/(1-n))**2 * diff_img_mag_err**2 )
    else:
        pos_or_neg = 1
        if 1+n <= 0.:
            diff_mag = 10**(-10)
            oid_mag_err = np.sqrt( 2**2 * temp_mag_err**2 + diff_img_mag_err**2 )
            flag = 1
        else:
            diff_mag = -2.5* np.log10(1+n)
            oid_mag_err = np.sqrt( (1-n/(1+n))**2 * temp_mag_err**2 + (n/(1+n))**2 * diff_img_mag_err**2 )
    oid_mag = diff_mag + temp_mag
    band = 'ztf_' + str(bands[band_id])

    data = {'mjd': obs_date, 'band': band, 'm_sci': oid_mag, 'm_sci_err': oid_mag_err, 'm_template': temp_mag, 'm_template_err': temp_mag_err, 
            'm_diff': diff_img_mag, 'm_diff_err': diff_img_mag_err, 'delta_m': diff_mag, 'pos_or_neg': pos_or_neg, 'm_sci_flag': flag}
    # data = pd.DataFrame(data=[[obs_date], [oid_mag], [oid_mag_err], [temp_mag], [temp_mag_err], [diff_img_mag], [diff_img_mag_err], [diff_mag], [pos_or_neg]], 
    #                                 columns = ['mjd', 'm_sci', 'm_sci_err', 'm_template', 'm_template_err', 'm_diff', 'm_diff_err', 'delta_m', 'pos_or_neg'])
    return data

#extract data
#m_sci is actually absolute magnitude
def ztf_alert2(alert):
    bands = ['x', 'g', 'R', 'i']
    
    band_id = alert.properties['ztf_fid']
    obs_date = float(alert.properties['ant_mjd'])
    ant_mag = alert.properties['ant_mag']
    temp_mag = alert.properties['ztf_magnr']
    temp_mag_err = alert.properties['ztf_sigmagnr']
    diff_img_mag = alert.properties['ztf_magpsf']
    diff_img_mag_err = alert.properties['ztf_sigmapsf']
    
    if alert.properties['ztf_isdiffpos'] == 'f' or alert.properties['ztf_isdiffpos'] == 0:
        pos_or_neg = -1
    else:
        pos_or_neg = 1

    oid_mag = -2.5*np.log(10**(-0.4*temp_mag) + pos_or_neg*10**(-0.4*diff_img_mag))
    diff_mag = abs(oid_mag - temp_mag)
    band = 'ztf_' + str(bands[band_id])
    data = {'mjd': obs_date, 'band': band, 'm_sci': oid_mag, 'm_template': temp_mag, 'm_diff': diff_img_mag, 
            'delta_m': diff_mag, 'pos_or_neg': pos_or_neg}
    return data


#unpacks all alerts (that pass a quality test)
def oid_get_info(alerts):
    new_alert = alerts[-1]

    #snr check
    if new_alert.properties['ant_survey'] == 1:
        if (1.0857/new_alert.properties['ztf_sigmapsf']) < 8:
            return 'snr too low'
        elif ztf_quality(new_alert) == True:
            oid = ztf_alert_err(new_alert)
        else:
            return 'failed ztf quality check'
    else:
        return 'alert not applicable'
            
    return oid

#catalog cross-matching
#provided mostly from jessie
def catalog_check(locus):
    flags = {'known_star': False, 'known_agn': False, 'known_galaxy': False, 'gaia_likely_star': False, 
                            'gaia_astro_star': False, 'ps1_pointlike': False}
    for cat in locus.catalog_objects:
        if cat == 'asassn_variable_catalog' or cat == 'asassn_variable_Catalog_v2_20190802' or cat == 'sdss_stars':
            flags['known_star'] = True
        if cat == 'veron_agn_qso' or cat == 'milliquas':
            flags['known_agn'] = True
        if cat == '2mass_xsc' or cat == 'nyu_valueadded_gals' or cat == 'sdss_gals' or cat == 'RC3':
            flags['known_galaxy'] = True
        if cat == 'gaia_dr3_gaia_source':
            if isinstance(locus.catalog_objects[cat][0]['classprob_dsc_combmod_star'], float) == 1 and locus.catalog_objects[cat][0]['classprob_dsc_combmod_star'] > 0.5:
                flags['gaia_likely_star'] = True
            if isinstance(locus.catalog_objects[cat][0]['parallax'], float) == 1:
                gdr3_check1 = (locus.catalog_objects[cat][0]['parallax'] + 0.017)/locus.catalog_objects[cat][0]['parallax_error']
                alpha = locus.catalog_objects[cat][0]['pmra']/locus.catalog_objects[cat][0]['pmra_error']
                beta = locus.catalog_objects[cat][0]['pmdec']/locus.catalog_objects[cat][0]['pmdec_error']
                gamma = locus.catalog_objects[cat][0]['pmra_pmdec_corr']
                gdr3_check2 = np.sqrt((alpha**2 + beta**2 -2*alpha*beta*gamma)/(1 - gamma**2))
                if gdr3_check1 > 5 or gdr3_check2 > 5:
                    flags['gaia_astro_star'] = True
        alert_temp = locus.alerts[-1].properties
        if alert_temp['ant_survey'] == 1 and ((alert_temp['ztf_sgscore1'] > 0.5 and alert_temp['ztf_distpsnr1'] < 1) or (alert_temp['ztf_sgscore2'] > 0.5 and alert_temp['ztf_distpsnr2'] < 1) or (alert_temp['ztf_sgscore3'] > 0.5 and alert_temp['ztf_distpsnr3'] < 1)):
            flags['ps1_pointlike'] = True
    return flags

#query ANTARES alert stream
#goes by 10x10 deg^2 chunks, retries until it happens
def query_by_chunk(mjd_start, mjd_end, ra_min, ra_max, dec_min, dec_max,
                   faint_lim=21, min_ndet=3, max_results=10000,
                   retries=3, wait=180):
    # set the query to fetch loci with alerts matching search criteria
    query = {
        "query": {
            "bool": {
                "filter": [
                    { "range": { "properties.newest_alert_observation_time": { "gte": mjd_start, "lte": mjd_end} } },
                    { "range": { "properties.brightest_alert_magnitude": {"lte": faint_lim} } },
                    { "range": { "properties.num_mag_values" : { "gte": 3} } },
                    { "range": { "ra": { "gte": ra_min, "lte": ra_max} } },
                    { "range": { "dec": { "gte": dec_min, "lte": dec_max} } }
                      ]
            }
        }
    }

    # sometimes the ANTARES server times out so try a few times
    # before giving up and returning an empty list (to avoid crashing the entire query)
    for attempt in range(retries):
        try:
            loci = list(search.search(query))
            if len(loci) >= max_results:
                warnings.warn(
                    f'Chunk MJD {mjd_start:.1f}–{mjd_end:.1f} hit the {max_results}-result max.'
                    f'— Reduce QUERY_DT or this window is incomplete.',
                    stacklevel=2
                )
            return get_ids(loci)
        except Exception as e:
            if attempt < retries - 1:
                print(f'  Chunk {mjd_start}–{mjd_end} failed (attempt {attempt+1}/{retries}): {e}.')
                time.sleep(15)
            else:
                time.sleep(wait)
                # pdb.set_trace()
                attempt = 0

#gets ids from a list of ANTARES loci objects
def get_ids(loci):
    # print(loci)
    loci_ids = []
    for locus in loci:
        loci_ids.append(locus.locus_id)
    return loci_ids

#gets info for ToO target generation, one oid at a time
def get_target_info(locus, oid):
    
    target = pd.DataFrame(columns = ['too_id','fiber_type','catalogid','sdss_id','gaia_dr3_source_id',
                                     'twomass_pts_key','sky_brightness_mode','ra','dec','pmra','pmdec',
                                     'epoch','parallax','lambda_eff','u_mag','g_mag','r_mag','i_mag','z_mag',
                                     'optical_prov','gaia_bp_mag','gaia_rp_mag','gaia_g_mag','h_mag',
                                     'delta_ra','delta_dec','can_offset','inertial','n_exposures','priority',
                                     'active','expiration_date','observed'])
    target.loc[0,'fiber_type'] = 'BOSS'
    for cat in locus.catalog_objects:
        if cat == 'sdss_gals':
            target.loc[0,'sdss_id'] = locus.catalog_objects[cat][0]['Objid']
        elif cat == 'sdss_stars':
            target.loc[0,'sdss_id'] = locus.catalog_objects[cat][0]['Objid']
        elif cat == 'gaia_dr3_gaia_source':
            target.loc[0,'gaia_dr3_source_id'] = locus.catalog_objects[cat][0]['Source Id']
        elif cat == '2mass_xsc':
            target.loc[0,'twomass_pts_key']= locus.catalog_objects[cat][0]['Id']

    target.loc[0,'sky_brightness_mode'] = 'dark'
    target.loc[0, 'ra'] = locus.ra
    target.loc[0,'dec'] = locus.dec

    
    passband = locus.alerts[-1].properties['ant_passband']
    if locus.alerts[-1].properties['ant_survey'] == 4: #lsst
        if passband == 'y':
            a  = 1
        else:
            target[passband+'_mag'].loc[0] = oid['lsst_'+passband]
    elif locus.alerts[-1].properties['ant_survey'] == 1:
        if passband == 'R':
            target.loc[0,'r_mag'] = oid['ztf_R']
        else:
            target.loc[0,passband+'_mag'] = oid['ztf_'+passband]

    target.loc[0, 'can_offset'] = True
    target.loc[0, 'n_exposures'] = 3
    target.loc[0, 'priority'] = 5
    target.loc[0, 'active'] = True
    target.loc[0, 'observed'] = False
    
    return target

#make lightcurve from all alerts in a locus
def lightcurve(alerts):
    lc = 0
    for alert in alerts:
        if alert.properties['ant_survey'] == 4:
            data = lsst_alert(alert)
        if alert.properties['ant_survey'] == 1:
            data = ztf_alert_err(alert)
        else:
            continue

        if isinstance(lc, int) == 1:
            lc = pd.DataFrame(data, index=[0])
        else:
            h = pd.DataFrame(data, index=[-1])
            lc = pd.concat([lc, h]).reset_index(drop=True)
        
    return lc

#make lightcuve from only quality alerts in a locus
def lightcurve_quality(alerts):
    lc = 0
    for alert in alerts:
        if alert.properties['ant_survey'] == 4:
            lsst_pass = lsst_quality(alert)
            if lsst_pass == True:
                data = lsst_alert(alert)
            else:
                continue
        elif alert.properties['ant_survey'] == 1:
            ztf_pass = ztf_quality(alert)
            if ztf_pass == True:
                data = ztf_alert_err(alert)
            else:
                continue
        else:
            continue
        
        if isinstance(lc, int) == 1:
            lc = pd.DataFrame(data, index=[0])
        else:
            h = pd.DataFrame(data, index=[-1])
            lc = pd.concat([lc, h]).reset_index(drop=True)

    return lc

#plot quality lightcurve for a given oid
def plot_lc(oid_id):
    colors = {'ztf_g': 'green', 'ztf_R': 'orangered', 'ztf_i': 'black'}
    fig, ax = plt.subplots(1,1, figsize=(9,6))
    
    locus = search.get_by_id(oid_id)
    lc = lightcurve_quality(locus.alerts)
    title = oid_id
    flags_str = 'Flags: '

    empty = 0
    
    for band in colors:
        band_data = lc[(lc['band'] == band)]
        if len(band_data) > 2:
            ax.errorbar(band_data['mjd'], band_data['m_sci'], yerr=band_data['m_sci_err'], fmt='.', ms=2, lw=1, 
                        c = colors[band], ecolor = colors[band], label=band, alpha = 0.5)
            ax.hlines(y=np.average(band_data['m_template']), xmin = locus.properties['oldest_alert_observation_time'], 
                      xmax= locus.properties['newest_alert_observation_time'], colors = colors[band], alpha = 0.3, ls = '--')
        else:
            empty += 1
            
    if empty == 3:
        print(f'{oid_id}: not enough data')
        plt.close()
    else:
        flags = catalog_check(locus)
        for flag in flags:
            if flags[flag] == True and len(flags_str) == 7:
                flags_str += flag
            elif flags[flag] == True:
                flags_str += ', ' + flag
        ax.set(ylim=(min(lc['m_sci'])-0.5, max(lc['m_sci'])+0.5))
        ax.yaxis.set_inverted(True)
        ax.legend(bbox_to_anchor=(1.02, 1), loc='upper left', borderaxespad=0.)
    
        if len(flags_str) > 7:
            fig.suptitle(title + '\n' + flags_str + '\nmessed up alerts: ' + str(sum(lc['m_sci_flag'])), fontname = 'serif')
        else:
            fig.suptitle(title + '\n' + flags_str + 'None\nmessed up alerts: ' + str(sum(lc['m_sci_flag'])), fontname = 'serif')
        plt.xlabel('MJD', fontname = 'serif')
        ax.set_ylabel('$mag_{AB}$', fontname = 'serif')
        ax.grid(alpha=0.25)
        plt.tight_layout()


def plot_lc2(oid_id):
    colors = {'ztf_g': 'green', 'ztf_R': 'orangered', 'ztf_i': 'black'}
    fig, ax = plt.subplots(1,2, figsize=(10,4), sharey=False)
    
    locus = search.get_by_id(oid_id)
    lc = lightcurve(locus.alerts)
    lc_q = lightcurve_quality(locus.alerts)
    title = oid_id
    flags_str = 'Flags: '

    empty = 0
    empty_q = 0
    
    for band in colors:
        band_data = lc[(lc['band'] == band)]
        band_data_q = lc_q[(lc_q['band'] == band)]
        if len(band_data) > 2:
            ax[0].errorbar(band_data['mjd'], band_data['m_sci'], yerr=band_data['m_sci_err'], fmt='.', ms=2, lw=1, c = colors[band], ecolor = colors[band], label=band, alpha = 0.5)
            ax[0].hlines(y=np.average(band_data['m_template']), xmin = locus.properties['oldest_alert_observation_time'], xmax= locus.properties['newest_alert_observation_time'], 
                          colors = colors[band], alpha = 0.3, ls = '--')
        else:
            empty += 1
        if len(band_data_q) > 2:
            ax[1].errorbar(band_data_q['mjd'], band_data_q['m_sci'], yerr=band_data_q['m_sci_err'], fmt='.', ms=2, lw=1, c = colors[band], ecolor = colors[band], label=band, alpha = 0.5)
            ax[1].hlines(y=np.average(band_data_q['m_template']), xmin = locus.properties['oldest_alert_observation_time'], xmax= locus.properties['newest_alert_observation_time'], 
                          colors = colors[band], alpha = 0.3, ls = '--')
        else:
            empty_q += 1
    
    if empty == 3:
        print(f'{oid_id}: not enough data')
        plt.close()
    else:
        flags = catalog_check(locus)
        for flag in flags:
            if flags[flag] == True and len(flags_str) == 7:
                flags_str += flag
            elif flags[flag] == True:
                flags_str += ', ' + flag
        ax[0].set(ylim=(min(lc['m_sci'])-0.5, max(lc['m_sci'])+0.5))
        ax[1].set(ylim=(min(lc_q['m_sci'])-0.5, max(lc_q['m_sci'])+0.5))
        ax[0].yaxis.set_inverted(True)
        ax[1].yaxis.set_inverted(True)
        ax[1].legend(bbox_to_anchor=(1.02, 1), loc='upper left', borderaxespad=0.)
    
        if len(flags_str) > 7:
            fig.suptitle(title + '\n' + flags_str + '\nmessed up alerts: ' + str(sum(lc['m_sci_flag'])) + ', ' + str(sum(lc_q['m_sci_flag'])), fontname = 'serif')
        else:
            fig.suptitle(title + '\n' + flags_str + 'None\nmessed up alerts: ' + str(sum(lc['m_sci_flag'])) + ', ' + str(sum(lc_q['m_sci_flag'])), fontname = 'serif')
        plt.xlabel('MJD', fontname = 'serif')
        ax[0].set_ylabel('$mag_{AB}$', fontname = 'serif')
        ax[1].set_ylabel('$mag_{AB}$', fontname = 'serif')
        ax[0].grid(alpha=0.25)
        ax[1].grid(alpha=0.25)
        plt.tight_layout()